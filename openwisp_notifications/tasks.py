from celery import shared_task
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from openwisp_notifications.swapper import load_model
from django.util import timezone
from datetime import timedelta

Notification = load_model('Notification')


@shared_task
def delete_obsolete_notifications(instance_app_label, instance_model, instance_id):
    """
    Delete notifications having 'instance' as actor, action or target object.
    """
    instance_content_type = ContentType.objects.get_by_natural_key(
        instance_app_label, instance_model
    )
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
def delete_old_notifications(days):
    """
    Delete notifications having 'timestamp' more than 90 days, task scheduled for every day.
    """
    where = (
        Q(timestamp=timezone.now() - timedelta(days=days))
    )
    Notification.objects.filter(where).delete()

