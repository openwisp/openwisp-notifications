from io import StringIO
from unittest.mock import patch

import swapper
from django.core import mail, management
from django.test import TestCase

from openwisp_notifications import checks
from openwisp_notifications import settings as app_settings
from openwisp_notifications.swapper import load_model
from openwisp_users.tests.utils import TestOrganizationMixin

Notification = load_model("Notification")
NotificationSetting = load_model("NotificationSetting")
Organization = swapper.load_model("openwisp_users", "Organization")


class TestManagementCommands(TestCase, TestOrganizationMixin):
    def test_create_notification_command(self):
        admin = self._get_admin()
        default_org = Organization.objects.first()
        cases = [
            {
                "name": "email enabled",
                "web": True,
                "email": True,
                "verified": True,
                "secondary": False,
                "notifications": 1,
                "emails": 1,
            },
            {
                "name": "email disabled",
                "web": True,
                "email": False,
                "verified": True,
                "secondary": False,
                "notifications": 1,
                "emails": 0,
            },
            {
                "name": "unverified email",
                "web": True,
                "email": True,
                "verified": False,
                "secondary": False,
                "notifications": 1,
                "emails": 0,
            },
            {
                "name": "verified secondary email only",
                "web": True,
                "email": True,
                "verified": False,
                "secondary": True,
                "notifications": 1,
                "emails": 0,
            },
            {
                "name": "web and email disabled",
                "web": False,
                "email": False,
                "verified": True,
                "secondary": False,
                "notifications": 0,
                "emails": 0,
            },
        ]
        for case in cases:
            with self.subTest(case["name"]):
                Notification.objects.all().delete()
                NotificationSetting.objects.filter(user=admin).delete()
                mail.outbox.clear()
                admin.emailaddress_set.exclude(email=admin.email).delete()
                admin.emailaddress_set.update(verified=case["verified"])
                if case["secondary"]:
                    admin.emailaddress_set.create(
                        email="secondary@example.com", verified=True, primary=False
                    )
                NotificationSetting.objects.create(
                    user=admin,
                    organization=default_org,
                    type="generic_message",
                    web=case["web"],
                    email=case["email"],
                )
                management.call_command("create_notification")
                self.assertEqual(
                    Notification.objects.count(),
                    case["notifications"],
                    msg="Unexpected number of notifications created",
                )
                self.assertEqual(
                    len(mail.outbox),
                    case["emails"],
                    msg="Unexpected number of emails sent",
                )
                if case["notifications"]:
                    n = Notification.objects.first()
                    self.assertEqual(n.type, "generic_message")
                    self.assertEqual(n.actor, default_org)
                    self.assertEqual(n.recipient, admin)

    @patch(
        "openwisp_notifications.tasks.ns_register_unregister_notification_type.delay"
    )
    def test_populate_notification_preferences_command(self, mocked_task):
        management.call_command("populate_notification_preferences")
        mocked_task.assert_called_once()


class TestChecks(TestCase, TestOrganizationMixin):
    @patch.object(
        app_settings,
        "HOST",
        "https://example.com",
    )
    def test_cors_not_configured(self):
        # If INSTALLED_APPS not configured
        with patch.multiple(
            "openwisp_notifications.types",
            NOTIFICATION_TYPES={},
            NOTIFICATION_CHOICES=[],
        ), patch("openwisp_utils.admin_theme.menu.MENU", {}), self.modify_settings(
            INSTALLED_APPS={"remove": "corsheaders"}
        ), StringIO() as stderr:
            management.call_command("check", stderr=stderr)
            self.assertIn("django-cors-headers", stderr.getvalue())

        # If MIDDLEWARE not configured
        with patch.multiple(
            "openwisp_notifications.types",
            NOTIFICATION_TYPES={},
            NOTIFICATION_CHOICES=[],
        ), self.modify_settings(
            MIDDLEWARE={"remove": "corsheaders.middleware.CorsMiddleware"}
        ), StringIO() as stderr:
            management.call_command("check", stderr=stderr)
            self.assertIn("django-cors-headers", stderr.getvalue())

    def test_ow_object_notification_setting_improperly_configured(self):
        def run_check():
            return checks.check_ow_object_notification_widget_setting(None).pop()

        with self.subTest("Test setting is not a list"):
            with patch.object(app_settings, "IGNORE_ENABLED_ADMIN", tuple()):
                error_message = (
                    '"OPENWISP_NOTIFICATIONS_IGNORE_ENABLED_ADMIN" should be a list'
                )
                error = run_check()
                self.assertIn(error_message, error.hint)

        with self.subTest("Test setting does not contains dotted path string"):
            with patch.object(app_settings, "IGNORE_ENABLED_ADMIN", [0]):
                error_message = (
                    '"OPENWISP_NOTIFICATIONS_IGNORE_ENABLED_ADMIN" should contain '
                    "dotted path string to ModelAdmin"
                )
                error = run_check()
                self.assertIn(error_message, error.hint)

        with self.subTest("Test setting dotted path is invalid"):
            path = "openwisp_notifications.admin.DeviceAdmin"
            with patch.object(app_settings, "IGNORE_ENABLED_ADMIN", [path]):
                error_message = (
                    f'Failed to import "{path}" defined in '
                    '"OPENWISP_NOTIFICATIONS_IGNORE_ENABLED_ADMIN".'
                )
                error = run_check()
                self.assertIn(error_message, error.hint)

        with self.subTest("Test setting dotted path is not subclass of ModelAdmin"):
            path = "openwisp_users.admin.OrganizationUserInline"
            with patch.object(app_settings, "IGNORE_ENABLED_ADMIN", [path]):
                error_message = (
                    f'"{path}" does not subclasses "django.contrib.admin.ModelAdmin"'
                )
                error = run_check()
                self.assertIn(error_message, error.hint)
