import openwisp_notifications.settings as app_settings
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.functional import cached_property
from django.utils.html import mark_safe, strip_tags
from django.utils.translation import ugettext_lazy as _
from markdown import markdown
from notifications.base.models import AbstractNotification
from openwisp_notifications.types import (
    NOTIFICATION_CHOICES,
    get_notification_configuration,
)
from openwisp_notifications.utils import _get_object_link
from swapper import swappable_setting

from openwisp_utils.base import TimeStampedEditableModel, UUIDModel

User = get_user_model()


class Notification(UUIDModel, AbstractNotification):
    COUNT_CACHE_KEY = 'ow2-unread-notifications-{0}'
    type = models.CharField(max_length=30, null=True, choices=NOTIFICATION_CHOICES)

    class Meta(AbstractNotification.Meta):
        abstract = False
        app_label = 'openwisp_notifications'
        swappable = swappable_setting('openwisp_notifications', 'Notification')

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
                self, field='actor', html=False, url_only=True, absolute_url=True
            )
            self.action_link = _get_object_link(
                self,
                field='action_object',
                html=False,
                url_only=True,
                absolute_url=True,
            )
            self.target_link = _get_object_link(
                self, field='target', html=False, url_only=True, absolute_url=True
            )

            config = get_notification_configuration(self.type)
            if 'message' in config:
                md_text = config['message'].format(notification=self)
            else:
                md_text = render_to_string(
                    config['message_template'], context=dict(notification=self)
                ).strip()
            # clean up
            self.actor_link = self.action_link = self.target_link = None
            return mark_safe(markdown(md_text))
        else:
            return self.description

    @cached_property
    def email_subject(self):
        if self.type:
            config = get_notification_configuration(self.type)
            return config['email_subject'].format(
                site=Site.objects.get_current(), notification=self
            )
        elif self.data.get('email_subject', None):
            return self.data.get('email_subject')
        else:
            return self.message


class NotificationUser(TimeStampedEditableModel):
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
        verbose_name = _('user notification settings')
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        if not self.receive:
            self.email = self.receive
        return super(NotificationUser, self).save(*args, **kwargs)


User = get_user_model()


@receiver(post_save, sender=User, dispatch_uid='create_notificationuser')
def create_notificationuser_settings(sender, instance, **kwargs):
    try:
        instance.notificationuser
    except ObjectDoesNotExist:
        NotificationUser.objects.create(user=instance)


@receiver(post_save, sender=Notification, dispatch_uid='send_email_notification')
def send_email_notification(sender, instance, created, **kwargs):
    # ensure we need to sending email or stop
    if not created or (
        not instance.recipient.notificationuser.email or not instance.recipient.email
    ):
        return
    # send email
    subject = instance.email_subject
    url = instance.data.get('url', '') if instance.data else None
    description = instance.message
    if url:
        target_url = url
    elif instance.target:
        target_url = _get_object_link(
            instance, field='target', html=False, url_only=True, absolute_url=True
        )
    else:
        target_url = None
    if target_url:
        description += '\n\nFor more information see {0}.'.format(target_url)
    mail = EmailMultiAlternatives(
        subject=subject,
        body=strip_tags(description),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[instance.recipient.email],
    )
    if app_settings.OPENWISP_NOTIFICATION_HTML_EMAIL:
        html_message = render_to_string(
            app_settings.OPENWISP_NOTIFICATION_EMAIL_TEMPLATE,
            context=dict(
                OPENWISP_NOTIFICATION_EMAIL_LOGO=app_settings.OPENWISP_NOTIFICATION_EMAIL_LOGO,
                notification=instance,
                target_url=target_url,
            ),
        )
        mail.attach_alternative(html_message, 'text/html')
    mail.send()
    # flag as emailed
    instance.emailed = True
    instance.save()


@receiver(post_save, sender=Notification, dispatch_uid='clear_notification_cache_saved')
@receiver(
    post_delete, sender=Notification, dispatch_uid='clear_notification_cache_deleted'
)
def clear_notification_cache(sender, instance, **kwargs):
    Notification.invalidate_cache(instance.recipient)
