from datetime import timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.db.models import Q
from django.db.utils import OperationalError
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from openwisp_notifications import settings as app_settings
from openwisp_notifications import types
from openwisp_notifications.swapper import load_model, swapper_load_model
from openwisp_notifications.utils import send_notification_email
from openwisp_utils.admin_theme.email import send_email
from openwisp_utils.tasks import OpenwispCeleryTask

EMAIL_BATCH_INTERVAL = app_settings.EMAIL_BATCH_INTERVAL

User = get_user_model()

Notification = load_model('Notification')
NotificationSetting = load_model('NotificationSetting')
IgnoreObjectNotification = load_model('IgnoreObjectNotification')

Organization = swapper_load_model('openwisp_users', 'Organization')
OrganizationUser = swapper_load_model('openwisp_users', 'OrganizationUser')


@shared_task(base=OpenwispCeleryTask)
def delete_obsolete_objects(instance_app_label, instance_model, instance_id):
    """
    Delete Notification and IgnoreObjectNotification objects having
    instance' as related objects..
    """
    try:
        instance_content_type = ContentType.objects.get_by_natural_key(
            instance_app_label, instance_model
        )
    except ContentType.DoesNotExist:
        return
    else:
        # Delete Notification objects
        where = (
            Q(actor_content_type=instance_content_type)
            | Q(action_object_content_type=instance_content_type)
            | Q(target_content_type=instance_content_type)
        )
        where = where & (
            Q(actor_object_id=instance_id)
            | Q(action_object_object_id=instance_id)
            | Q(target_object_id=instance_id)
        )
        Notification.objects.filter(where).delete()

        # Delete IgnoreObjectNotification objects
        try:
            IgnoreObjectNotification.objects.filter(
                object_id=instance_id, object_content_type_id=instance_content_type.pk
            ).delete()
        except OperationalError:
            # Raised when an object is deleted in migration
            return


@shared_task(base=OpenwispCeleryTask)
def delete_notification(notification_id):
    Notification.objects.filter(pk=notification_id).delete()


@shared_task
def delete_old_notifications(days):
    """
    Delete notifications having 'timestamp' more than "days" days.
    """
    Notification.objects.filter(
        timestamp__lte=timezone.now() - timedelta(days=days)
    ).delete()


# Following tasks updates notification settings in database.
# 'ns' is short for notification_setting
def create_notification_settings(user, organizations, notification_types):
    for type in notification_types:
        for org in organizations:
            NotificationSetting.objects.update_or_create(
                defaults={'deleted': False}, user=user, type=type, organization=org
            )


@shared_task(base=OpenwispCeleryTask)
def update_superuser_notification_settings(instance_id, is_superuser, is_created):
    """
    Adds notification setting for all notification types and organizations.
    If a superuser gets demoted, flags it's notification settings as deleted.
    """
    user = User.objects.get(pk=instance_id)

    # When a user is demoted from superuser status,
    # only keep notification settings for organization they are member of.
    if not (is_superuser or is_created):
        NotificationSetting.objects.filter(user_id=instance_id).exclude(
            organization__in=user.organizations_managed
        ).update(deleted=True)
        return

    if not is_superuser:
        return

    # Create notification settings for superuser
    create_notification_settings(
        user=user,
        organizations=Organization.objects.all(),
        notification_types=types.NOTIFICATION_TYPES.keys(),
    )


@shared_task(base=OpenwispCeleryTask)
def ns_register_unregister_notification_type(
    notification_type=None, delete_unregistered=True
):
    """
    Creates notification setting for registered notification types.
    Deletes notification for unregistered notification types.
    """

    notification_types = (
        [notification_type] if notification_type else types.NOTIFICATION_TYPES.keys()
    )

    organizations = Organization.objects.all()
    # Create notification settings for superusers
    for user in User.objects.filter(is_superuser=True).iterator():
        create_notification_settings(user, organizations, notification_types)

    # Create notification settings for organization admin
    for org_user in OrganizationUser.objects.select_related(
        'user', 'organization'
    ).filter(is_admin=True, user__is_superuser=False):
        create_notification_settings(
            org_user.user, [org_user.organization], notification_types
        )

    if delete_unregistered:
        # Delete all notification settings for unregistered notification types
        NotificationSetting.objects.exclude(type__in=notification_types).update(
            deleted=True
        )
        # Delete notifications related to unregister notification types
        Notification.objects.exclude(type__in=notification_types).delete()


@shared_task(base=OpenwispCeleryTask)
def update_org_user_notificationsetting(org_user_id, user_id, org_id, is_org_admin):
    """
    Adds notification settings for all notification types when a new
    organization user is added.
    """
    user = User.objects.get(pk=user_id)
    if not user.is_superuser:
        # The following query covers conditions for change in admin status
        # and organization field of related OrganizationUser objects
        NotificationSetting.objects.filter(user=user).exclude(
            organization_id__in=user.organizations_managed
        ).update(deleted=True)

    if not is_org_admin:
        return

    # Create new notification settings
    organization = Organization.objects.get(id=org_id)
    create_notification_settings(
        user=user,
        organizations=[organization],
        notification_types=types.NOTIFICATION_TYPES.keys(),
    )


@shared_task(base=OpenwispCeleryTask)
def ns_organization_user_deleted(user_id, org_id):
    """
    Deletes notification settings for all notification types when
    an organization user is deleted.
    """
    NotificationSetting.objects.filter(user_id=user_id, organization_id=org_id).update(
        deleted=True
    )


@shared_task(base=OpenwispCeleryTask)
def ns_organization_created(instance_id):
    """
    Adds notification setting of all registered types
    for a newly created organization.
    """
    organization = Organization.objects.get(id=instance_id)
    for user in User.objects.filter(is_superuser=True):
        create_notification_settings(
            user=user,
            organizations=[organization],
            notification_types=types.NOTIFICATION_TYPES.keys(),
        )


@shared_task(base=OpenwispCeleryTask)
def delete_ignore_object_notification(instance_id):
    """
    Deletes IgnoreObjectNotification object post it's expiration.
    """
    IgnoreObjectNotification.objects.filter(id=instance_id).delete()


@shared_task(base=OpenwispCeleryTask)
def batch_email_notification(email_id):
    """
    Sends a summary of notifications to the specified email address.
    """
    ids = cache.get(f'{email_id}_batch_pks', [])

    if not ids:
        return

    unsent_notifications = Notification.objects.filter(id__in=ids)
    notifications_count = unsent_notifications.count()
    current_site = Site.objects.get_current()

    if notifications_count == 1:
        instance = unsent_notifications.first()
        send_notification_email(instance)
    else:
        alerts = []
        for notification in unsent_notifications:
            url = notification.data.get('url', '') if notification.data else None
            if url:
                target_url = url
            elif notification.target:
                target_url = notification.redirect_view_url
            else:
                target_url = None

            description = notification.message if notifications_count <= 5 else None
            alerts.append(
                {
                    'level': notification.level,
                    'message': notification.message,
                    'description': description,
                    'timestamp': notification.timestamp,
                    'url': target_url,
                }
            )

        context = {
            'alerts': alerts,
            'notifications_count': notifications_count,
            'site_name': current_site.name,
            'site_domain': current_site.domain,
        }
        html_content = render_to_string('emails/batch_email.html', context)
        plain_text_content = strip_tags(html_content)

        extra_context = {}
        if notifications_count > 5:
            extra_context = {
                'call_to_action_url': f"https://{current_site.domain}/admin",
                'call_to_action_text': 'View all Notifications',
            }

        send_email(
            subject=f'Summary of {notifications_count} Notifications',
            body_text=plain_text_content,
            body_html=html_content,
            recipients=[email_id],
            extra_context=extra_context,
        )
    unsent_notifications.update(emailed=True)
    Notification.objects.bulk_update(unsent_notifications, ['emailed'])
    cache.delete(f'{email_id}_pks')
