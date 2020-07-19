from asgiref.sync import async_to_sync
from channels import layers
from openwisp_notifications.api.serializers import NotificationListSerializer


def notification_update_handler(reload_widget=False, notification=None, recipient=None):
    channel_layer = layers.get_channel_layer()
    if notification:
        notification = NotificationListSerializer(notification).data
    async_to_sync(channel_layer.group_send)(
        'ow_notification',
        {
            'type': 'send.updates',
            'reload_widget': reload_widget,
            'notification': notification,
            'recipient': str(recipient.pk),
        },
    )
