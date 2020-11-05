from openwisp_notifications.swapper import load_model, swapper_load_model
from openwisp_notifications.tests.test_admin import TestAdmin as BaseTestAdmin
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
from openwisp_notifications.tests.test_utils import TestChecks as BaseTestChecks
from openwisp_notifications.tests.test_utils import (
    TestManagementCommands as BaseTestManageCommands,
)

Notification = load_model('Notification')


class TestAdmin(BaseTestAdmin):
    app_label = 'sample_notifications'


class TestNotifications(BaseTestNotifications):
    # Used only for testing openwisp-notifications
    def test_test_app_object_created_notification(self):
        from ..models import TestApp

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
del BaseTestNotifications
del BaseTestNotificationApi
del BaseTestNotificationSetting
del BaseTestIgnoreObjectNotification
