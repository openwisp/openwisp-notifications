import os
import subprocess
import sys

from django.conf import settings
from django.test import SimpleTestCase


class TestASGIStartup(SimpleTestCase):
    def test_fresh_process_initializes_app_registry(self):
        # A fresh interpreter catches imports that only work after django.setup().
        for sample_app in ("", "1"):
            with self.subTest(sample_app=sample_app):
                env = os.environ.copy()
                env.update(
                    DJANGO_SETTINGS_MODULE="openwisp2.settings",
                    SAMPLE_APP=sample_app,
                    PYTHONPATH=os.pathsep.join(
                        filter(
                            None,
                            [os.path.dirname(settings.BASE_DIR), env.get("PYTHONPATH")],
                        )
                    ),
                )
                result = subprocess.run(
                    [
                        sys.executable,
                        "-c",
                        "from openwisp2.asgi import application; "
                        "from django.apps import apps; "
                        "assert apps.ready; "
                        "assert set(application.application_mapping) == "
                        "{'http', 'websocket'}",
                    ],
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
