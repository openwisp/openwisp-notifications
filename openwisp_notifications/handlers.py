from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.db.models.query import QuerySet
from django.db.models.signals import (
    post_delete,
    post_migrate,
    post_save,
    pre_delete,
    pre_save,
)
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from openwisp_notifications import settings as app_settings
from openwisp_notifications import tasks
from openwisp_notifications.exceptions import NotificationRenderException
from openwisp_notifications.swapper import load_model, swapper_load_model
from openwisp_notifications.types import get_notification_configuration
from openwisp_notifications.websockets import handlers as ws_handlers

EXTRA_DATA = app_settings.get_config()['USE_JSONFIELD']

User = get_user_model()

Notification = load_model('Notification')
NotificationSetting = load_model('NotificationSetting')
NotificationsAppConfig = apps.get_app_config(NotificationSetting._meta.app_label)

Group = swapper_load_model('openwisp_users', 'Group')
OrganizationUser = swapper_load_model('openwisp_users', 'OrganizationUser')
Organization = swapper_load_model('openwisp_users', 'Organization')


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
        org_admin_query = Q(
            openwisp_users_organizationuser__organization=target_org,
            openwisp_users_organizationuser__is_admin=True,
        )
        where = where | (Q(is_staff=True) & org_admin_query)
        where_group = org_admin_query

        # We can only find notification setting if notification type and
        # target organization is present.
        if notification_type:
            # Create notification for users who have opted for receiving notifications.
            # For users who have not configured web_notifications,
            # use default from notification type
            web_notification = Q(notificationsetting__web=True)
            if notification_template['web_notification']:
                web_notification |= Q(notificationsetting__web=None)

            notification_setting = web_notification & Q(
                notificationsetting__type=notification_type,
                notificationsetting__organization_id=target_org,
            )
            where = where & notification_setting
            where_group = where_group & notification_setting

    # Ensure notifications are only sent to active user
    where = where & Q(is_active=True)
    where_group = where_group & Q(is_active=True)

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
            User.objects.prefetch_related('notificationsetting_set')
            .order_by('date_joined')
            .filter(where)
        )

    optional_objs = [
        (kwargs.pop(opt, None), opt) for opt in ('target', 'action_object')
    ]

    notification_list = []
    for recipient in recipients:
        notification = Notification(
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
                setattr(notification, '%s_object_id' % opt, obj.pk)
                setattr(
                    notification,
                    '%s_content_type' % opt,
                    ContentType.objects.get_for_model(obj),
                )
        if kwargs and EXTRA_DATA:
            notification.data = kwargs
        notification.save()
        notification_list.append(notification)

    return notification_list


@receiver(post_save, sender=Notification, dispatch_uid='send_email_notification')
def send_email_notification(sender, instance, created, **kwargs):
    # Abort if a new notification is not created
    if not created:
        return
    # Get email preference of user for this type of notification.
    target_org = getattr(getattr(instance, 'target', None), 'organization_id', None)
    if instance.type and target_org:
        notification_setting = instance.recipient.notificationsetting_set.get(
            organization=target_org, type=instance.type
        )
        email_preference = notification_setting.email_notification
    else:
        # We can not check email preference if notification type is absent,
        # or if target_org is not present
        # therefore send email anyway.
        email_preference = True

    if not (email_preference and instance.recipient.email):
        return

    try:
        subject = instance.email_subject
    except NotificationRenderException:
        # Do not send email if notification is malformed.
        return
    url = instance.data.get('url', '') if instance.data else None
    description = instance.message
    if url:
        target_url = url
    elif instance.target:
        target_url = instance.redirect_view_url
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
    # Reload notification only if notification is created or deleted
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
        tasks.delete_obsolete_notifications.delay(
            instance_app_label, instance_model, instance_id
        )


@receiver(
    post_migrate,
    sender=NotificationsAppConfig,
    dispatch_uid='register_unregister_notification_types',
)
def notification_type_registered_unregistered_handler(sender, **kwargs):
    tasks.ns_register_unregister_notification_type.delay()


@receiver(
    pre_save,
    sender=OrganizationUser,
    dispatch_uid='create_orguser_notification_setting',
)
def notification_setting_org_user_created(instance, **kwargs):
    if instance.is_admin:
        tasks.ns_organization_user_added_or_updated.delay(
            instance_id=instance.pk,
            instance_user_id=instance.user_id,
            instance_org_id=instance.organization_id,
        )


@receiver(
    post_delete,
    sender=OrganizationUser,
    dispatch_uid='delete_orguser_notification_setting',
)
def notification_setting_delete_org_user(instance, **kwargs):
    tasks.ns_organization_user_deleted.delay(
        instance_user_id=instance.user_id, instance_org_id=instance.organization_id
    )


@receiver(post_save, sender=User, dispatch_uid='user_notification_setting')
def notification_setting_user_created(instance, created, **kwargs):
    tasks.ns_user_created.delay(instance.pk, instance.is_superuser, created)


@receiver(
    post_save, sender=Organization, dispatch_uid='org_created_notification_setting'
)
def notification_setting_org_created(created, instance, **kwargs):
    if created:
        tasks.ns_organization_created.delay(instance.pk)
