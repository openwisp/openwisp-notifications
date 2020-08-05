from unittest.mock import patch

from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from openwisp_notifications import settings as app_settings
from openwisp_notifications.signals import notify
from openwisp_notifications.swapper import load_model

from openwisp_users.tests.utils import TestOrganizationMixin

from .test_helpers import MessagingRequest

Notification = load_model('Notification')
notification_queryset = Notification.objects.order_by('-timestamp')


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

    app_label = 'openwisp_notifications'

    def _login_admin(self):
        u = User.objects.create_superuser('admin', 'admin', 'test@test.com')
        self.client.force_login(u)
        return u

    def setUp(self):
        self.admin = self._login_admin()
        self.notification_options = dict(
            sender=self.admin,
            recipient=self.admin,
            description='Test Notification',
            verb='Test Notification',
            email_subject='Test Email subject',
            url='localhost:8000/admin',
        )
        self.site = AdminSite()

    @property
    def _url(self):
        return reverse('admin:index')

    def _expected_output(self, count=None):
        if count:
            return '<span id="ow-notification-count">{0}</span>'.format(count)
        return f'id="{self.app_label}">'

    def test_zero_notifications(self):
        r = self.client.get(self._url)
        self.assertContains(r, self._expected_output())

    def test_non_zero_notifications(self):
        patched_function = 'openwisp_notifications.templatetags.notification_tags.base_notification_unread'
        with self.subTest("Test UI for less than 100 notifications"):
            with patch(patched_function, return_value=10):
                r = self.client.get(self._url)
                self.assertContains(r, self._expected_output('10'))

        Notification.invalidate_unread_cache(self.admin)

        with self.subTest("Test UI for 99+ notifications"):
            with patch(patched_function, return_value=100):
                r = self.client.get(self._url)
                self.assertContains(r, self._expected_output('99+'))

    def test_cached_value(self):
        self.client.get(self._url)
        cache_key = Notification.count_cache_key(self.admin.pk)
        self.assertEqual(cache.get(cache_key), 0)
        return cache_key

    def test_cached_invalidation(self):
        cache_key = self.test_cached_value()
        notify.send(**self.notification_options)
        self.assertIsNone(cache.get(cache_key))
        self.client.get(self._url)
        self.assertEqual(cache.get(cache_key), 1)

    def test_default_notification_setting(self):
        res = self.client.get(self._url)
        self.assertContains(
            res, '/static/openwisp-notifications/audio/notification_bell.mp3'
        )
        self.assertContains(res, 'window.location')

    @patch.object(
        app_settings, 'OPENWISP_NOTIFICATIONS_SOUND', '/static/notification.mp3',
    )
    def test_notification_sound_setting(self):
        res = self.client.get(self._url)
        self.assertContains(res, '/static/notification.mp3')
        self.assertNotContains(
            res, '/static/openwisp-notifications/audio/notification_bell.mp3'
        )

    @patch.object(
        app_settings, 'OPENWISP_NOTIFICATIONS_HOST', 'https://example.com',
    )
    def test_notification_host_setting(self):
        res = self.client.get(self._url)
        self.assertContains(res, 'https://example.com')
        self.assertNotContains(res, 'window.location')

    def test_jquery_import(self):
        response = self.client.get(self._url)
        self.assertInHTML(
            '<script type="text/javascript" src="/static/admin/js/jquery.init.js">',
            str(response.content),
            1,
        )
        self.assertInHTML(
            '<script type="text/javascript" src="/static/admin/js/vendor/jquery/jquery.min.js">',
            str(response.content),
            1,
        )

        response = self.client.get(reverse('admin:sites_site_changelist'))
        self.assertInHTML(
            '<script type="text/javascript" src="/static/admin/js/jquery.init.js">',
            str(response.content),
            1,
        )
        self.assertInHTML(
            '<script type="text/javascript" src="/static/admin/js/vendor/jquery/jquery.min.js">',
            str(response.content),
            1,
        )

    def test_login_load_javascript(self):
        self.client.logout()
        response = self.client.get(reverse('admin:login'))
        self.assertNotContains(response, 'notifications.js')

    def test_websocket_protocol(self):
        with self.subTest('Test in production environment'):
            response = self.client.get(self._url)
            self.assertContains(response, 'wss')

        with self.subTest('Test in development environment'):
            with self.settings(DEBUG=True, INTERNAL_IPS=['127.0.0.1']):
                response = self.client.get(self._url)
                self.assertNotContains(response, 'wss')
                self.assertContains(response, 'ws')
