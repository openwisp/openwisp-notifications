from datetime import datetime

from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import HttpRequest
from django.utils import timezone

from openwisp_notifications.swapper import load_model
from openwisp_notifications.tasks import ns_register_unregister_notification_type
from openwisp_notifications.types import (
    register_notification_type as base_register_notification_type,
)
from openwisp_notifications.types import (
    unregister_notification_type as base_unregister_notification_type,
)

NotificationSetting = load_model('NotificationSetting')

TEST_DATETIME = datetime(2020, 5, 4, 0, 0, 0, 0, timezone.get_default_timezone())


class MessagingRequest(HttpRequest):
    session = 'session'

    def __init__(self):
        super(MessagingRequest, self).__init__()
        self._messages = FallbackStorage(self)

    def get_messages(self):
        return getattr(self._messages, '_queued_messages')

    def get_message_strings(self):
        return [str(m) for m in self.get_messages()]


def register_notification_type(type_name, type_config, models=[]):
    base_register_notification_type(type_name, type_config, models)
    ns_register_unregister_notification_type.delay(
        notification_type=type_name, delete_unregistered=False
    )


def unregister_notification_type(type_name):
    base_unregister_notification_type(type_name)
    NotificationSetting.objects.filter(type=type_name).update(deleted=True)
