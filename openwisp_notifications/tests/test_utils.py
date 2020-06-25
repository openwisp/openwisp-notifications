import swapper
from django.core import management
from django.test import TestCase
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
