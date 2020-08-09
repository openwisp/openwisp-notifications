from datetime import timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils import timezone

from openwisp_notifications.swapper import load_model, swapper_load_model
from openwisp_notifications.types import NOTIFICATION_TYPES

User = get_user_model()

Notification = load_model('Notification')
NotificationSetting = load_model('NotificationSetting')

Organization = swapper_load_model('openwisp_users', 'Organization')
OrganizationUser = swapper_load_model('openwisp_users', 'OrganizationUser')


@shared_task
def delete_obsolete_notifications(instance_app_label, instance_model, instance_id):
    """
    Delete notifications having 'instance' as actor, action or target object.
    """
    try:
        instance_content_type = ContentType.objects.get_by_natural_key(
            instance_app_label, instance_model
        )
    except ContentType.DoesNotExist:
        return
    else:
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


@shared_task
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
@shared_task
def ns_user_created(instance_id, is_superuser, is_created):
    """
    Adds notification setting for all notification types
    and organizations.
    """

    # When a user is demoted from superuser status,
    # only keep notification settings for organization they are member of.
    if not (is_superuser or is_created):
        orgs_membership = OrganizationUser.objects.filter(
            user_id=instance_id, is_admin=True, user__is_staff=True
        ).values('organization')
        NotificationSetting.objects.filter(user_id=instance_id).exclude(
            organization__in=orgs_membership
        ).delete()
        return

    notification_types = NOTIFICATION_TYPES.keys()

    notification_settings = []
    for type in notification_types:
        if is_superuser:
            for org in Organization.objects.iterator():
                notification_settings.append(
                    NotificationSetting(
                        user_id=instance_id, type=type, organization=org
                    )
                )

    NotificationSetting.objects.bulk_create(
        notification_settings, ignore_conflicts=True
    )


@shared_task
def ns_register_unregister_notification_type(
    notification_type=None, delete_unregistered=True
):
    """
    Creates notification setting for registered notification types.
    Deletes notification for unregistered notification types.
    """

    notification_types = (
        [notification_type] if notification_type else NOTIFICATION_TYPES.keys()
    )
    notification_settings = []

    for type in notification_types:
        for user in User.objects.filter(is_superuser=True):
            # Superusers receives notifications for all organizations
            # irrespective of their membership.
            for org in Organization.objects.iterator():
                notification_settings.append(
                    NotificationSetting(user=user, type=type, organization=org)
                )

        # OrganizationUsers receives notifications for organization they
        # are member of.
        for org_user in OrganizationUser.objects.filter(
            is_admin=True, user__is_staff=True
        ).iterator():
            notification_settings.append(
                NotificationSetting(
                    user_id=org_user.user_id,
                    organization_id=org_user.organization_id,
                    type=type,
                )
            )

    NotificationSetting.objects.bulk_create(
        notification_settings, ignore_conflicts=True
    )

    if delete_unregistered:
        # Delete all notification settings for unregistered notification types
        NotificationSetting.objects.exclude(type__in=notification_types).delete()
        # Delete notifications related to unregister notification types
        Notification.objects.exclude(type__in=notification_types).delete()


@shared_task
def ns_organization_user_added_or_updated(
    instance_id, instance_user_id, instance_org_id
):
    """
    Adds notification settings for all notification types when a new
    organization user is added.
    """
    # If OrganizationUser's organization is updated then,
    # delete notification setttings related to old organizations.
    old_organization = OrganizationUser.objects.filter(pk=instance_id).values(
        'organization'
    )
    NotificationSetting.objects.filter(organization_id__in=old_organization).delete()

    # Create new notification settings
    notification_settings = []
    for notification_type in NOTIFICATION_TYPES.keys():
        notification_settings.append(
            NotificationSetting(
                user_id=instance_user_id,
                organization_id=instance_org_id,
                type=notification_type,
            )
        )

    NotificationSetting.objects.bulk_create(
        notification_settings, ignore_conflicts=True
    )


@shared_task
def ns_organization_user_deleted(instance_user_id, instance_org_id):
    """
    Deletes notification settings for all notification types when
    an organization user is deleted.
    """
    NotificationSetting.objects.filter(
        user_id=instance_user_id, organization_id=instance_org_id
    ).delete()


@shared_task
def ns_organization_created(instance_id):
    """
    Adds notification setting of all registered types
    for a newly created organization.
    """
    notification_types = NOTIFICATION_TYPES.keys()
    notification_settings = []
    for user in User.objects.filter(is_superuser=True):
        for type in notification_types:
            notification_settings.append(
                NotificationSetting(
                    user_id=user.id, type=type, organization_id=instance_id
                )
            )
    NotificationSetting.objects.bulk_create(
        notification_settings, ignore_conflicts=True
    )
