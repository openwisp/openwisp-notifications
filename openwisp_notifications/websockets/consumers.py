import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from openwisp_notifications.utils import normalize_unread_count


class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        try:
            assert self.scope['user'].is_authenticated is True
        except (KeyError, AssertionError):
            self.close()
        else:
            async_to_sync(self.channel_layer.group_add)(
                "ow_notification", self.channel_name
            )
            self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            "ow_notification", self.channel_name
        )

    def notification_update_widget(self, event):
        user = self.scope['user']
        # Send message only if notification belongs to current user
        if event['recipient'] == str(user.pk):
            unread_notifications = normalize_unread_count(
                user.notifications.unread().count()
            )
            self.send(
                json.dumps(
                    {
                        'notification_count': unread_notifications,
                        'reload_widget': event['reload_widget'],
                        'notification': event['notification'],
                    }
                )
            )
