from swapper import swappable_setting

from openwisp_notifications.base.models import (
    AbstractNotification,
    AbstractNotificationUser,
)


class Notification(AbstractNotification):
    class Meta(AbstractNotification.Meta):
        abstract = False
        app_label = 'openwisp_notifications'
        swappable = swappable_setting('openwisp_notifications', 'Notification')


class NotificationUser(AbstractNotificationUser):
    class Meta(AbstractNotificationUser.Meta):
        abstract = False
        swappable = swappable_setting('openwisp_notifications', 'NotificationUser')
