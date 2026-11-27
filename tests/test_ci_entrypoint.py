"""Check that the CI test entry point rejects unsupported arguments."""

import os
import runpy
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

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
        runner = runpy.run_path(str(ROOT / "runtests.py"))["run_focused_tests"]
        for label, sample in (
            ("openwisp_notifications.tests.test_notifications", ""),
            ("openwisp2.sample_notifications.tests.test_django", "1"),
        ):
            with self.subTest(label=label), patch.dict(
                os.environ, {"SAMPLE_APP": ""}
            ), patch.object(sys, "argv", ["runtests.py"]), patch(
                "django.setup"
            ), patch.dict(
                runner.__globals__, {"validate_test_labels": lambda labels: None}
            ):
                runner([label, "--noinput"])
                self.assertEqual(os.environ["SAMPLE_APP"], sample)
                self.assertEqual(sys.argv[1:], ["test", label, "--noinput"])

    def test_focused_test_failure_exit_is_preserved(self):
        label = "openwisp_notifications.tests.test_notifications"
        with patch.object(sys, "argv", ["runtests.py", "--focused", label]), patch(
            "django.setup"
        ), patch("openwisp_utils.test.runner.validate_test_labels"), patch(
            "django.core.management.execute_from_command_line",
            side_effect=SystemExit(7),
        ), self.assertRaises(
            SystemExit
        ) as result:
            runpy.run_path(str(ROOT / "runtests.py"), run_name="__main__")
        self.assertEqual(result.exception.code, 7)


if __name__ == "__main__":
    unittest.main()
