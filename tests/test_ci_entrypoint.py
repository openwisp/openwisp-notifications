"""Check that the CI test entry point rejects unsupported arguments."""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestCiEntrypoint(unittest.TestCase):
    def test_rejects_unsupported_arguments(self):
        for arguments in (
            ("--settings=other",),
            ("--testrunner=other.Runner",),
            ("--noinput",),
            ("os.system",),
            ("openwisp_notifications.tests.test_missing",),
            ("openwisp_notifications.tests.test_websockets",),
            (
                "openwisp_notifications.tests.test_models",
                "openwisp2.sample_notifications.tests.test_django",
            ),
        ):
            with self.subTest(arguments=arguments):
                result = subprocess.run(
                    ["./runtests", *arguments],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn("Unsupported test argument", result.stderr)

    def test_pytest_uses_test_settings(self):
        code = (
            "import runpy, sys; "
            "sys.argv = ['pytest', 'openwisp_notifications/tests/test_websockets.py']; "
            "assert runpy.run_path('tests/openwisp2/settings.py')['TESTING']"
        )
        result = subprocess.run(
            ["python", "-c", code],
            cwd=ROOT,
            env={**os.environ, "TESTING": "1"},
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_focused_labels_select_their_configuration(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copy2(ROOT / "runtests", root / "runtests")
            shutil.copy2(ROOT / "runtests.py", root / "runtests.py")
            (root / "django" / "core").mkdir(parents=True)
            (root / "openwisp_notifications" / "tests").mkdir(parents=True)
            (root / "tests" / "openwisp2" / "sample_notifications" / "tests").mkdir(
                parents=True
            )
            for package in (
                root / "django",
                root / "django" / "core",
                root / "openwisp_notifications",
                root / "openwisp_notifications" / "tests",
                root / "tests" / "openwisp2",
                root / "tests" / "openwisp2" / "sample_notifications",
                root / "tests" / "openwisp2" / "sample_notifications" / "tests",
            ):
                (package / "__init__.py").touch()
            (root / "django" / "__init__.py").write_text("def setup(): pass\n")
            (root / "django" / "core" / "management.py").write_text(
                "import json, os, sys\n"
                "def execute_from_command_line(args):\n"
                '    print(json.dumps({"sample": os.environ.get("SAMPLE_APP"), '
                '"args": args[1:]}))\n'
                '    if os.environ.get("FAIL_TEST"): sys.exit(7)\n'
            )
            for module in (
                root / "openwisp_notifications" / "tests" / "test_probe.py",
                root
                / "tests"
                / "openwisp2"
                / "sample_notifications"
                / "tests"
                / "test_probe.py",
            ):
                module.write_text(
                    "import unittest\n"
                    "class TestProbe(unittest.TestCase):\n"
                    "    def test_ok(self): pass\n"
                )
            for label, sample in (
                ("openwisp_notifications.tests.test_probe.TestProbe.test_ok", ""),
                (
                    "openwisp2.sample_notifications.tests.test_probe.TestProbe.test_ok",
                    "1",
                ),
            ):
                with self.subTest(label=label):
                    env = {**os.environ, "SAMPLE_APP": ""}
                    result = subprocess.run(
                        [str(root / "runtests"), label, "--noinput"],
                        cwd=root,
                        env=env,
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(
                        json.loads(result.stdout),
                        {"sample": sample, "args": ["test", label, "--noinput"]},
                    )
                    failed = subprocess.run(
                        [str(root / "runtests"), label],
                        cwd=root,
                        env={**env, "FAIL_TEST": "1"},
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(failed.returncode, 7, failed.stderr)


if __name__ == "__main__":
    unittest.main()
