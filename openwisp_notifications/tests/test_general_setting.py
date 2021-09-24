from django.test import TestCase

from openwisp_notifications.signals import notify
from openwisp_notifications.swapper import load_model
from openwisp_users.tests.utils import TestOrganizationMixin

GeneralSetting = load_model('GeneralSetting')
Notification = load_model('Notification')
on_queryset = Notification.objects


class TestDisableNotifications(TestOrganizationMixin, TestCase):
    def setUp(self):
        self.admin = self._get_admin()
        self.org1 = self._get_org()

    def test_disable_only_email_notifications(self):
        '''
        notification is created and it have emailed = False
        '''
        GeneralSetting.objects.create(user=self.admin, email=True, web=False)
        notify.send(sender=self.admin, type='default', target=self.org1)
        self.assertEqual(on_queryset.count(), 1)
        notification = on_queryset.all()[0]
        self.assertEqual(notification.emailed, False)

    def test_disable_only_web_notifications(self):
        '''
        notification is not created when web notifications
        are disabled
        '''
        GeneralSetting.objects.create(user=self.admin, email=False, web=True)
        notify.send(sender=self.admin, type='default', target=self.org1)
        self.assertEqual(on_queryset.count(), 0)

    def test_disable_all_notifications(self):
        '''
        notification is not created when all notifications
        are disabled
        '''
        GeneralSetting.objects.create(user=self.admin, email=True, web=True)
        notify.send(sender=self.admin, type='default', target=self.org1)
        self.assertEqual(on_queryset.count(), 0)

        # test when other organizations are created
        org2 = self._create_org(name='test org 2', slug='test-org-2')
        notify.send(sender=self.admin, type='default', target=org2)
        self.assertEqual(on_queryset.count(), 0)
