from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.db.models.query import QuerySet
from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from openwisp_notifications import settings as app_settings
from openwisp_notifications.swapper import load_model
from openwisp_notifications.tasks import delete_obsolete_notifications
from openwisp_notifications.types import get_notification_configuration
from openwisp_notifications.utils import NotificationException, _get_object_link
from openwisp_notifications.websockets import handlers as ws_handlers

User = get_user_model()

EXTRA_DATA = app_settings.get_config()['USE_JSONFIELD']

Notification = load_model('Notification')
NotificationUser = load_model('NotificationUser')


def notify_handler(**kwargs):
    """
    Handler function to create Notification instance upon action signal call.
    """
    # Pull the options out of kwargs
    kwargs.pop('signal', None)
    actor = kwargs.pop('sender')
    public = bool(kwargs.pop('public', True))
    description = kwargs.pop('description', None)
    timestamp = kwargs.pop('timestamp', timezone.now())
    recipient = kwargs.pop('recipient', None)
    notification_type = kwargs.pop('type', None)
    notification_template = get_notification_configuration(notification_type)
    level = notification_template.get(
        'level', kwargs.pop('level', Notification.LEVELS.info)
    )
    verb = notification_template.get('verb', kwargs.pop('verb', None))
    target_org = getattr(kwargs.get('target', None), 'organization_id', None)

    where = Q(is_superuser=True)
    where_group = Q()
    if target_org:
        where = where | (Q(is_staff=True) & Q(openwisp_users_organization=target_org))
        where_group = Q(openwisp_users_organization=target_org)
    where_group = where_group & Q(notificationuser__receive=True)
    where = where & Q(notificationuser__receive=True)

    if recipient:
        # Check if recipient is User, Group or QuerySet
        if isinstance(recipient, Group):
            recipients = recipient.user_set.filter(where_group)
        elif isinstance(recipient, (QuerySet, list)):
            recipients = recipient
        else:
            recipients = [recipient]
    else:
        recipients = (
            User.objects.select_related('notificationuser')
            .order_by('date_joined')
            .filter(where)
        )

    optional_objs = [
        (kwargs.pop(opt, None), opt) for opt in ('target', 'action_object')
    ]

    new_notifications = []
    for recipient in recipients:
        newnotify = Notification(
            recipient=recipient,
            actor=actor,
            verb=str(verb),
            public=public,
            description=description,
            timestamp=timestamp,
            level=level,
            type=notification_type,
        )

        # Set optional objects
        for obj, opt in optional_objs:
            if obj is not None:
                setattr(newnotify, '%s_object_id' % opt, obj.pk)
                setattr(
                    newnotify,
                    '%s_content_type' % opt,
                    ContentType.objects.get_for_model(obj),
                )
        if kwargs and EXTRA_DATA:
            newnotify.data = kwargs
        newnotify.save()
        new_notifications.append(newnotify)

    return new_notifications


@receiver(post_save, sender=User, dispatch_uid='create_notificationuser')
def create_notificationuser_settings(sender, instance, **kwargs):
    try:
        instance.notificationuser
    except ObjectDoesNotExist:
        NotificationUser.objects.create(user=instance)


@receiver(post_save, sender=Notification, dispatch_uid='send_email_notification')
def send_email_notification(sender, instance, created, **kwargs):
    # Abort if new notification is not created or
    # notification recipient opted out of email notifications
    if not created or not (
        instance.recipient.notificationuser.email and instance.recipient.email
    ):
        return
    try:
        subject = instance.email_subject
    except NotificationException:
        # Do not send email if notification is malformed.
        return
    url = instance.data.get('url', '') if instance.data else None
    description = instance.message
    if url:
        target_url = url
    elif instance.target:
        target_url = _get_object_link(
            instance, field='target', url_only=True, absolute_url=True
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
    if app_settings.OPENWISP_NOTIFICATIONS_HTML_EMAIL:
        html_message = render_to_string(
            app_settings.OPENWISP_NOTIFICATIONS_EMAIL_TEMPLATE,
            context=dict(
                OPENWISP_NOTIFICATIONS_EMAIL_LOGO=app_settings.OPENWISP_NOTIFICATIONS_EMAIL_LOGO,
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
    try:
        Notification.invalidate_unread_cache(instance.recipient)
    except AttributeError:
        return
    # Reload notification only if notification is created or deleleted
    # Display when a new notification is created
    ws_handlers.notification_update_handler(
        recipient=instance.recipient,
        reload_widget=kwargs.get('created', True),
        notification=instance if kwargs.get('created', None) else None,
    )


@receiver(pre_delete, dispatch_uid='notification_related_object_deleted')
def notification_related_object_deleted(sender, instance, **kwargs):
    """
    Delete notifications having 'instance' as actor, action or target object.
    """
    instance_id = getattr(instance, 'pk', None)
    if instance_id:
        instance_model = instance._meta.model_name
        instance_app_label = instance._meta.app_label
        delete_obsolete_notifications.delay(
            instance_app_label, instance_model, instance_id
        )
