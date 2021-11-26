from asgiref.sync import async_to_sync
from channels import layers
from django.core.cache import cache
from django.utils.timezone import now, timedelta

from openwisp_notifications.api.serializers import NotFound, NotificationListSerializer

from ..swapper import load_model

Notification = load_model('Notification')


def user_in_notification_storm(user):
    in_notification_storm = cache.get(f'ow-noti-storm-{user.pk}', False)
    if in_notification_storm:
        return True
    qs = Notification.objects.filter(recipient=user)
    if qs.filter(timestamp__gte=now() - timedelta(seconds=10)).count() >= 6:
        in_notification_storm = True
    elif qs.filter(timestamp__gte=now() - timedelta(seconds=60)).count() >= 30:
        in_notification_storm = True
    if in_notification_storm:
        cache.set(f'ow-noti-storm-{user.pk}', True, 60)
    return in_notification_storm


def notification_update_handler(reload_widget=False, notification=None, recipient=None):
    channel_layer = layers.get_channel_layer()
    try:
        assert notification is not None
        notification = NotificationListSerializer(notification).data
    except (NotFound, AssertionError):
        pass
    async_to_sync(channel_layer.group_send)(
        'ow_notification',
        {
            'type': 'send.updates',
            'reload_widget': reload_widget,
            'notification': notification,
            'recipient': str(recipient.pk),
            'in_notification_storm': user_in_notification_storm(recipient),
        },
    )
