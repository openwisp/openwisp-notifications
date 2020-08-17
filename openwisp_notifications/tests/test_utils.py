from io import StringIO
from unittest.mock import patch

import swapper
from django.core import management
from django.test import TestCase

from openwisp_notifications import settings as app_settings
from openwisp_notifications.swapper import load_model
from openwisp_users.tests.utils import TestOrganizationMixin

Notification = load_model('Notification')
Organization = swapper.load_model('openwisp_users', 'Organization')


class TestUtils(TestCase, TestOrganizationMixin):
    def test_create_notification_command(self):
        admin = self._get_admin()
        management.call_command('create_notification')
        default_org = Organization.objects.first()

        self.assertEqual(Notification.objects.count(), 1)
        n = Notification.objects.first()
        self.assertEqual(n.type, 'default')
        self.assertEqual(n.actor, default_org)
        self.assertEqual(n.recipient, admin)

    @patch.object(
        app_settings, 'OPENWISP_NOTIFICATIONS_HOST', 'https://example.com',
    )
    def test_cors_not_configured(self):
        # If INSTALLED_APPS not configured
        with self.modify_settings(
            INSTALLED_APPS={'remove': 'corsheaders'}
        ), StringIO() as stderr:
            management.call_command('check', stderr=stderr)
            self.assertIn('django-cors-headers', stderr.getvalue())

        # If MIDDLEWARE not configured
        with self.modify_settings(
            MIDDLEWARE={'remove': 'corsheaders.middleware.CorsMiddleware'}
        ), StringIO() as stderr:
            management.call_command('check', stderr=stderr)
            self.assertIn('django-cors-headers', stderr.getvalue())
