import swapper
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from openwisp_notifications.signals import notify

from openwisp_users.tests.utils import TestOrganizationMixin

from ..admin import NotificationAdmin
from .test_helpers import MessagingRequest

Notification = swapper.load_model('openwisp_notifications', 'Notification')
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
        self.model_admin = NotificationAdmin(Notification, self.site)

    _url = reverse('admin:openwisp_notifications_notification_changelist')
    _cache_key = Notification.COUNT_CACHE_KEY

    def _expected_output(self, count=None):
        if count:
            return '<span>{0}</span>'.format(count)
        return 'id="openwisp-notifications">'

    def test_zero_notifications(self):
        r = self.client.get(self._url)
        self.assertContains(r, self._expected_output())

    def test_non_zero_notifications(self):
        with self.subTest("Test UI for less than 100 notifications"):
            no_of_notifications = 10
            for _ in range(no_of_notifications):
                notify.send(**self.notification_options)
            r = self.client.get(self._url)
            self.assertContains(r, self._expected_output('10'))

        with self.subTest("Test UI for 99+ notifications"):
            no_of_notifications = 100
            for _ in range(no_of_notifications):
                notify.send(**self.notification_options)
            r = self.client.get(self._url)
            self.assertContains(r, self._expected_output('99+'))

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

    def _generic_test_obj_link(self, field):
        notify.send(**self.notification_options)
        n = notification_queryset.first()
        get_actual_obj_link = getattr(self.model_admin, f'{field}_object_link')
        object_id = getattr(n, f'{field}_object_id', None)

        exp_obj_link = '<a href="{0}" id="{1}-object-url">{2}</a>'.format(
            reverse('admin:openwisp_users_user_change', args=(object_id,)),
            field,
            object_id,
        )
        self.assertEqual(get_actual_obj_link(n), exp_obj_link)

        setattr(n, f'{field}_content_type', ContentType())
        self.assertEqual(get_actual_obj_link(n), object_id)

        setattr(n, f'{field}_content_type', None)
        self.assertEqual(get_actual_obj_link(n), '-')

    def test_callable_actor_object_link(self):
        self._generic_test_obj_link('actor')

    def test_callable_action_object_link(self):
        self.notification_options.update({'action_object': self.admin})
        self._generic_test_obj_link('action_object')

    def test_callable_target_object_link(self):
        self.notification_options.update({'target': self.admin})
        self._generic_test_obj_link('target')

    def test_callable_related_object(self):
        self.notification_options.update({'target': self.admin})
        notify.send(**self.notification_options)
        n = notification_queryset.first()

        exp_related_obj_link = '<a href="{0}" id="related-object-url">{1}: {2}</a>'.format(
            reverse('admin:openwisp_users_user_change', args=(self.admin.id,)),
            ContentType.objects.get_for_model(self.admin).model,
            self.admin,
        )
        self.assertEqual(self.model_admin.related_object(n), exp_related_obj_link)

        n.target_content_type = ContentType()
        self.assertEqual(self.model_admin.related_object(n), n.target_object_id)

        n.target_content_type = None
        self.assertEqual(self.model_admin.related_object(n), '-')

    def test_notification_view_webpage(self):
        notify.send(**self.notification_options)
        n = notification_queryset.first()
        url = reverse('admin:openwisp_notifications_notification_change', args=(n.id,))
        response = self.client.get(url)
        self.assertContains(response, 'id="actor-object-url"')
        self.assertContains(response, '<div class="readonly">Test Notification</div>')
