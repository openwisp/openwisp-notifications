import swapper
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from openwisp_notifications.signals import notify

from openwisp_users.tests.utils import TestOrganizationMixin

from ..admin import NotificationAdmin
from .test_helpers import MessagingRequest

Notification = swapper.load_model('openwisp_notifications', 'Notification')


class MockSuperUser:
    def has_perm(self, perm):
        return True

    @property
    def pk(self):
        return 1


User = get_user_model()
request = MessagingRequest()
request.user = MockSuperUser()


class TestAdmin(TestOrganizationMixin, TestCase):
    """
    Tests notifications in admin
    """

    def _login_admin(self):
        u = User.objects.create_superuser('admin', 'admin', 'test@test.com')
        self.client.force_login(u)
        return u

    def setUp(self):
        self.admin = self._login_admin()
        self.notification_options = dict(
            sender=self.admin,
            recipient=self.admin,
            description="Test Notification",
            verb="Test Notification",
            email_subject='Test Email subject',
            url='localhost:8000/admin',
        )
        self.site = AdminSite()
        self.model_admin = NotificationAdmin(Notification, self.site)

    _url = reverse('admin:openwisp_notifications_notification_changelist')
    _cache_key = Notification.COUNT_CACHE_KEY

    def _expected_output(self, count=0):
        if count > 0:
            return '<span>{0}</span>'.format(count)
        return 'id="openwisp-notifications">'

    def test_zero_notifications(self):
        r = self.client.get(self._url)
        self.assertContains(r, self._expected_output())

    def test_non_zero_notifications(self):
        no_of_notifications = 10
        for _ in range(no_of_notifications):
            notify.send(**self.notification_options)
        r = self.client.get(self._url)
        self.assertContains(r, self._expected_output(no_of_notifications))

    def test_cached_value(self):
        self.client.get(self._url)
        cache_key = self._cache_key.format(self.admin.pk)
        self.assertEqual(cache.get(cache_key), 0)
        return cache_key

    def test_cached_invalidation(self):
        cache_key = self.test_cached_value()
        notify.send(**self.notification_options)
        self.assertIsNone(cache.get(cache_key))
        self.client.get(self._url)
        self.assertEqual(cache.get(cache_key), 1)

    def test_mark_as_read_action(self):
        notify.send(**self.notification_options)
        qs = Notification.objects.all()
        self.model_admin.mark_as_read(request, qs)
        self.assertEqual(qs.count(), 1)
        m = list(request.get_messages())
        self.assertEqual(len(m), 1)
        self.assertEqual(str(m[0]), '1 notification was marked as read.')
