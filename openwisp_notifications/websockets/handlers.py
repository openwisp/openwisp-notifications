from asgiref.sync import async_to_sync
from channels import layers
from django.utils.timezone import now, timedelta

from openwisp_notifications.api.serializers import NotFound, NotificationListSerializer

from ..swapper import load_model

Notification = load_model('Notification')


def notification_update_handler(reload_widget=False, notification=None, recipient=None):
    channel_layer = layers.get_channel_layer()
    try:
        assert notification is not None
        notification = NotificationListSerializer(notification).data
    except (NotFound, AssertionError):
        pass
    is_notification_storm = reload_widget and (
        Notification.objects.filter(
            recipient=recipient,
            timestamp__gte=now() - timedelta(10),
        ).count()
        > 10
    )
    async_to_sync(channel_layer.group_send)(
        'ow_notification',
        {
            'type': 'send.updates',
            'reload_widget': reload_widget,
            'notification': notification,
            'recipient': str(recipient.pk),
            'is_notification_storm': is_notification_storm,
        },
    )
