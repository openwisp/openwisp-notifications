# isort:skip_file
from django.db import models
from openwisp_notifications.base.models import (
    AbstractNotification,
    AbstractNotificationSetting,
)

# Only for testing openwisp_notifications

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from swapper import get_model_name

from openwisp_notifications.signals import notify

from openwisp_utils.base import UUIDModel


class DetailsModel(models.Model):
    details = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        abstract = True


class Notification(DetailsModel, AbstractNotification):
    class Meta(AbstractNotification.Meta):
        abstract = False
        app_label = 'sample_notifications'


class NotificationSetting(DetailsModel, AbstractNotificationSetting):
    class Meta(AbstractNotificationSetting.Meta):
        abstract = False


class TestApp(UUIDModel):
    name = models.CharField(max_length=50)
    organization = models.ForeignKey(
        get_model_name('openwisp_users', 'Organization'), on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _('Test App')
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


@receiver(post_save, sender=TestApp, dispatch_uid='test_app_object_created')
def test_app_model_notification(sender, instance, created, **kwargs):
    if created:
        notify.send(sender=instance, type='object_created', target=instance)
