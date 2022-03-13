from unittest.mock import patch

from django.apps.registry import apps
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache

from openwisp_notifications.swapper import load_model, swapper_load_model
from openwisp_notifications.tests.test_admin import TestAdmin as BaseTestAdmin
from openwisp_notifications.tests.test_admin import TestAdminMedia as BaseTestAdminMedia
from openwisp_notifications.tests.test_api import (
    TestNotificationApi as BaseTestNotificationApi,
)
from openwisp_notifications.tests.test_ignore_object_notification import (
    TestIgnoreObjectNotification as BaseTestIgnoreObjectNotification,
)
from openwisp_notifications.tests.test_notification_setting import (
    TestNotificationSetting as BaseTestNotificationSetting,
)
from openwisp_notifications.tests.test_notifications import (
    TestNotifications as BaseTestNotifications,
)
from openwisp_notifications.tests.test_notifications import (
    TestTransactionNotifications as BaseTestTransactionNotifications,
)
from openwisp_notifications.tests.test_utils import TestChecks as BaseTestChecks
from openwisp_notifications.tests.test_utils import (
    TestManagementCommands as BaseTestManageCommands,
)

from ..models import TestApp

Notification = load_model('Notification')
NotificationAppConfig = apps.get_app_config(Notification._meta.app_label)


class TestAdmin(BaseTestAdmin):
    app_label = 'sample_notifications'


class TestAdminMedia(BaseTestAdminMedia):
    pass


class TestNotifications(BaseTestNotifications):
    # Used only for testing openwisp-notifications
    def test_app_object_created_notification(self):
        OrganizationUser = swapper_load_model('openwisp_users', 'OrganizationUser')

        org = self._get_org()
        operator = self._get_operator()
        OrganizationUser.objects.create(user=operator, organization=org, is_admin=True)
        oum_obj = TestApp(organization=org, name='Test')
        oum_obj.save()

        n = Notification.objects.get(type='object_created', recipient=operator)
        n_count = Notification.objects.count()
        self.assertEqual(n_count, 2)
        self.assertEqual(n.actor, oum_obj)
        self.assertEqual(n.target, oum_obj)
        self.assertEqual(n.message, '<p>Test object created.</p>')
        n.delete()

    @patch.object(
        NotificationAppConfig, 'register_notification_types', return_value=None
    )
    def test_post_migrate_populate_notification_settings(self, *args):
        super().test_post_migrate_populate_notification_settings()


class TestTransactionNotifications(BaseTestTransactionNotifications):
    def _create_test_app(self):
        org = self._get_org()
        test_app = TestApp.objects.create(name='test_app', organization=org)
        return test_app

    def _get_test_app(self, test_app_name='test_app'):
        try:
            return TestApp.objects.get(name=test_app_name)
        except TestApp.DoesNotExist:
            return self._create_test_app()

    def test_test_app_cache_invalidation(self):
        test_app = self._get_test_app()
        content_type = ContentType.objects.get_for_model(test_app._meta.model)
        cache_key = Notification._cache_key(content_type.id, test_app.id)
        test_app_cache = cache.get(cache_key, None)
        self.assertEqual(test_app_cache.name, test_app.name)
        test_app.name = 'new test app'
        test_app.save()
        notification = Notification.objects.get(target_content_type=content_type)
        self.assertEqual(notification.target.name, test_app.name)
        test_app_cache = cache.get(cache_key, None)
        self.assertEqual(test_app_cache.name, test_app.name)


class TestNotificationAPI(BaseTestNotificationApi):
    pass


class TestNotificationSetting(BaseTestNotificationSetting):
    pass


class TestIgnoreObjectNotification(BaseTestIgnoreObjectNotification):
    pass


class TestManagementCommands(BaseTestManageCommands):
    pass


class TestChecks(BaseTestChecks):
    pass


del BaseTestAdmin
del BaseTestAdminMedia
del BaseTestNotifications
del BaseTestNotificationApi
del BaseTestNotificationSetting
del BaseTestIgnoreObjectNotification
