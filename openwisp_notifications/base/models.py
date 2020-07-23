import logging

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.db import models
from django.template.loader import render_to_string
from django.utils.functional import cached_property
from django.utils.html import mark_safe
from django.utils.translation import ugettext_lazy as _
from markdown import markdown
from notifications.base.models import AbstractNotification as BaseNotifcation
from openwisp_notifications import settings as app_settings
from openwisp_notifications.types import (
    NOTIFICATION_CHOICES,
    get_notification_configuration,
)
from openwisp_notifications.utils import NotificationException, _get_object_link

from openwisp_utils.base import TimeStampedEditableModel, UUIDModel

logger = logging.getLogger(__name__)


class AbstractNotification(UUIDModel, BaseNotifcation):
    CACHE_KEY_PREFIX = 'ow-notifications-'
    type = models.CharField(max_length=30, null=True, choices=NOTIFICATION_CHOICES)
    _actor = BaseNotifcation.actor
    _action_object = BaseNotifcation.action_object
    _target = BaseNotifcation.target

    class Meta(BaseNotifcation.Meta):
        abstract = True

    def __init__(self, *args, **kwargs):
        related_objs = [
            (opt, kwargs.pop(opt, None)) for opt in ('target', 'action_object', 'actor')
        ]
        super().__init__(*args, **kwargs)
        for opt, obj in related_objs:
            if obj is not None:
                setattr(self, f'{opt}_object_id', obj.pk)
                setattr(
                    self, f'{opt}_content_type', ContentType.objects.get_for_model(obj),
                )

    def __str__(self):
        return self.timesince()

    @classmethod
    def _cache_key(cls, *args):
        args = map(str, args)
        key = '-'.join(args)
        return f'{cls.CACHE_KEY_PREFIX}{key}'

    @classmethod
    def count_cache_key(cls, user_pk):
        return cls._cache_key(f'unread-{user_pk}')

    @classmethod
    def invalidate_unread_cache(cls, user):
        """
        Invalidate unread cache for user.
        """
        cache.delete(cls.count_cache_key(user.pk))

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

    def _related_object(self, field):
        obj_id = getattr(self, f'{field}_object_id')
        obj_content_type_id = getattr(self, f'{field}_content_type_id')
        if not obj_id:
            return
        cache_key = self._cache_key(obj_content_type_id, obj_id)
        obj = cache.get(cache_key)
        if not obj:
            obj = getattr(self, f'_{field}')
            cache.set(
                cache_key,
                obj,
                timeout=app_settings.OPENWISP_NOTIFICATIONS_CACHE_TIMEOUT,
            )
        return obj

    @cached_property
    def actor(self):
        return self._related_object('actor')

    @cached_property
    def action_object(self):
        return self._related_object('action_object')

    @cached_property
    def target(self):
        return self._related_object('target')


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
