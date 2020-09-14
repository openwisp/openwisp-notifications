import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.contenttypes.models import ContentType

from openwisp_notifications.api.serializers import IgnoreObjectNotificationSerializer
from openwisp_notifications.swapper import load_model
from openwisp_notifications.utils import normalize_unread_count

Notification = load_model('Notification')
IgnoreObjectNotification = load_model('IgnoreObjectNotification')


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
                        'type': 'notification',
                        'notification_count': unread_notifications,
                        'reload_widget': event['reload_widget'],
                        'notification': event['notification'],
                    }
                )
            )

    def receive(self, text_data):
        if self._is_user_authenticated():
            try:
                json_data = json.loads(text_data)
            except json.JSONDecodeError:
                return

            try:
                if json_data['type'] == 'notification':
                    self._notification_handler(
                        notification_id=json_data['notification_id']
                    )
                elif json_data['type'] == 'object_notification':
                    self._object_notification_handler(
                        object_id=json_data['object_id'],
                        app_label=json_data['app_label'],
                        model_name=json_data['model_name'],
                    )
            except KeyError:
                return

    def _notification_handler(self, notification_id):
        try:
            notification = Notification.objects.get(
                recipient=self.scope['user'], id=notification_id
            )
            notification.mark_as_read()
        except Notification.DoesNotExist:
            return

    def _object_notification_handler(self, object_id, app_label, model_name):
        try:
            object_notification = IgnoreObjectNotification.objects.get(
                user=self.scope['user'],
                object_id=object_id,
                object_content_type_id=ContentType.objects.get_by_natural_key(
                    app_label=app_label, model=model_name,
                ).pk,
            )
            serialized_data = IgnoreObjectNotificationSerializer(object_notification)
            self.send(
                json.dumps(
                    {
                        'type': 'object_notification',
                        'valid_till': serialized_data.data['valid_till'],
                    }
                )
            )
        except IgnoreObjectNotification.DoesNotExist:
            return
