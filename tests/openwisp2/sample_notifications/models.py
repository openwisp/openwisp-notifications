from django.db import models
from openwisp_notifications.base.models import (
    AbstractNotification,
    AbstractNotificationUser,
)


class DetailsModel(models.Model):
    details = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        abstract = True


class Notification(DetailsModel, AbstractNotification):
    class Meta(AbstractNotification.Meta):
        abstract = False
        app_label = 'sample_notifications'


class NotificationUser(DetailsModel, AbstractNotificationUser):
    details = models.CharField(max_length=64, blank=True, null=True)

    class Meta(AbstractNotificationUser.Meta):
        abstract = False
