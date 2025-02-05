from swapper import swappable_setting
from django.db import models
from django.conf import settings

from openwisp_notifications.base.models import (
    AbstractIgnoreObjectNotification,
    AbstractNotification,
    AbstractNotificationSetting,
)


class Notification(AbstractNotification):
    class Meta(AbstractNotification.Meta):
        abstract = False
        app_label = 'openwisp_notifications'
        swappable = swappable_setting('openwisp_notifications', 'Notification')


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


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    needs_verification = models.BooleanField(default=False)