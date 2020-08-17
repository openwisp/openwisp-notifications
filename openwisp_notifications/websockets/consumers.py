import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from openwisp_notifications.swapper import load_model
from openwisp_notifications.utils import normalize_unread_count

Notification = load_model('Notification')


class NotificationConsumer(WebsocketConsumer):
    def _is_user_authenticated(self):
        try:
            assert self.scope['user'].is_authenticated is True
        except (KeyError, AssertionError):
            self.close()
            return False
        else:
            return True

    def connect(self):
        if self._is_user_authenticated():
            async_to_sync(self.channel_layer.group_add)(
                'ow_notification', self.channel_name
            )
            self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            'ow_notification', self.channel_name
        )

    def send_updates(self, event):
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

    def receive(self, text_data):
        if self._is_user_authenticated():
            try:
                text_data_json = json.loads(text_data)
                notification_id = text_data_json['notification_id']
                notification = Notification.objects.get(
                    recipient=self.scope['user'], id=notification_id
                )
            except (json.JSONDecodeError, KeyError, Notification.DoesNotExist):
                pass
            else:
                notification.mark_as_read()
