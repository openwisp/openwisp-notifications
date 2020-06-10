from openwisp_notifications.swapper import load_model
from openwisp_notifications.tests.test_admin import TestAdmin as BaseTestAdmin
from openwisp_notifications.tests.test_notifications import (
    TestNotifications as BaseTestNotifications,
)

Notification = load_model('Notification')


class TestAdmin(BaseTestAdmin):
    app_label = 'sample_notifications'


class TestNotifications(BaseTestNotifications):
    app_label = 'sample_notifications'


del BaseTestAdmin
del BaseTestNotifications
