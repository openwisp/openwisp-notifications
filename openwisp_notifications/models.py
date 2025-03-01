from swapper import swappable_setting

from openwisp_notifications.base.models import (
    AbstractIgnoreObjectNotification,
    AbstractNotification,
    AbstractNotificationSetting,
)
from .types import get_notification_configuration


class Notification(AbstractNotification):
    class Meta(AbstractNotification.Meta):
        abstract = False
        app_label = 'openwisp_notifications'
        swappable = swappable_setting('openwisp_notifications', 'Notification')

    @property
    def notification_verb(self):
        """
        Returns notification verb from type configuration if verb is None,
        otherwise returns the stored verb
        """
        if self.verb is None and self.type:
            config = get_notification_configuration(self.type)
            return config.get('verb', '')
        return self.verb


class NotificationSetting(AbstractNotificationSetting):
    class Meta(AbstractNotificationSetting.Meta):
        abstract = False
        swappable = swappable_setting('openwisp_notifications', 'NotificationSetting')


class IgnoreObjectNotification(AbstractIgnoreObjectNotification):
    class Meta(AbstractIgnoreObjectNotification.Meta):
        abstract = False
        swappable = swappable_setting(
            'openwisp_notifications', 'IgnoreObjectNotification'
        )
