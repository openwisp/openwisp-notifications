import logging

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.db import models
from django.template.loader import render_to_string
from django.utils.functional import cached_property
from django.utils.html import mark_safe
from django.utils.translation import ugettext_lazy as _
from markdown import markdown
from notifications.base.models import AbstractNotification as BaseNotifcation
from openwisp_notifications.types import (
    NOTIFICATION_CHOICES,
    get_notification_configuration,
)
from openwisp_notifications.utils import NotificationException, _get_object_link

from openwisp_utils.base import TimeStampedEditableModel, UUIDModel

logger = logging.getLogger(__name__)


class AbstractNotification(UUIDModel, BaseNotifcation):
    COUNT_CACHE_KEY = 'ow2-unread-notifications-{0}'
    type = models.CharField(max_length=30, null=True, choices=NOTIFICATION_CHOICES)

    class Meta(BaseNotifcation.Meta):
        abstract = True

    def __str__(self):
        return self.timesince()

    @classmethod
    def invalidate_cache(cls, user):
        """ invalidate cache for user """
        cache.delete(cls.COUNT_CACHE_KEY.format(user.pk))

    @cached_property
    def message(self):
        if self.type:
            # setting links in notification object for message rendering
            self.actor_link = _get_object_link(
                self, field='actor', url_only=True, absolute_url=True
            )
            self.action_link = _get_object_link(
                self, field='action_object', url_only=True, absolute_url=True,
            )
            self.target_link = _get_object_link(
                self, field='target', url_only=True, absolute_url=True
            )

            config = get_notification_configuration(self.type)
            try:
                if 'message' in config:
                    md_text = config['message'].format(notification=self)
                else:
                    md_text = render_to_string(
                        config['message_template'], context=dict(notification=self)
                    ).strip()
            except AttributeError as e:
                logger.error(e)
                md_text = (
                    'Error while generating notification message,'
                    ' notification data may have been deleted.'
                )
            # clean up
            self.actor_link = self.action_link = self.target_link = None
            return mark_safe(markdown(md_text))
        else:
            return self.description

    @cached_property
    def email_subject(self):
        if self.type:
            try:
                config = get_notification_configuration(self.type)
                return config['email_subject'].format(
                    site=Site.objects.get_current(), notification=self
                )
            except AttributeError as e:
                logger.error(e)
                raise NotificationException('Error while generating notification')
        elif self.data.get('email_subject', None):
            return self.data.get('email_subject')
        else:
            return self.message


class AbstractNotificationUser(TimeStampedEditableModel):
    _RECEIVE_HELP = (
        'note: non-superadmin users receive '
        'notifications only for organizations '
        'of which they are member of.'
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    receive = models.BooleanField(
        _('receive notifications'), default=True, help_text=_(_RECEIVE_HELP)
    )
    email = models.BooleanField(
        _('email notifications'), default=True, help_text=_(_RECEIVE_HELP)
    )

    class Meta:
        abstract = True
        verbose_name = _('user notification settings')
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        if not self.receive:
            self.email = self.receive
        return super(AbstractNotificationUser, self).save(*args, **kwargs)
