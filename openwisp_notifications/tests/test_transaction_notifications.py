from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db.models.signals import post_save
from django.test import TransactionTestCase

from openwisp_notifications.handlers import register_notification_cache_update
from openwisp_notifications.signals import notify
from openwisp_notifications.swapper import load_model
from openwisp_users.tests.utils import TestOrganizationMixin

User = get_user_model()
Notification = load_model('Notification')


class TestTransactionNotifications(TestOrganizationMixin, TransactionTestCase):
    def setUp(self):
        self.admin = self._create_admin()
        self.notification_options = dict(
            sender=self.admin,
            description='Test Notification',
            level='info',
            verb='Test Notification',
            email_subject='Test Email subject',
            url='https://localhost:8000/admin',
        )

    def _create_notification(self):
        return notify.send(**self.notification_options)

    def _register_notification_cache_update(self, model, signal, dispatch_uid):
        register_notification_cache_update(model, signal, dispatch_uid=dispatch_uid)

    def test_notification_cache_update(self):
        operator = self._get_operator()
        self._register_notification_cache_update(
            User, post_save, 'operator_name_changed_invalidation'
        )
        self.notification_options.update(
            {'action_object': operator, 'target': operator, 'type': 'default'}
        )
        self._create_notification()
        content_type = ContentType.objects.get_for_model(operator._meta.model)
        cache_key = Notification._cache_key(content_type.id, operator.id)
        operator_cache = cache.get(cache_key, None)
        self.assertEqual(operator_cache.username, operator.username)
        operator.username = 'new operator name'
        operator.save()
        notification = Notification.objects.get(target_content_type=content_type)
        operator_cache = cache.get(cache_key, None)
        self.assertEqual(notification.target.username, 'new operator name')
