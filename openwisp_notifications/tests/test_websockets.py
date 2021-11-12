import uuid
from unittest.mock import patch

import pytest
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils.module_loading import import_string

from openwisp_notifications.api.serializers import NotificationListSerializer
from openwisp_notifications.signals import notify
from openwisp_notifications.swapper import load_model
from openwisp_notifications.tests.test_helpers import TEST_DATETIME

User = get_user_model()
Notification = load_model('Notification')
IgnoreObjectNotification = load_model('IgnoreObjectNotification')


@database_sync_to_async
def create_notification(admin_user):
    n = notify.send(sender=admin_user, type='default').pop()
    return n[1].pop()


@database_sync_to_async
def notification_operation(notification, **kwargs):
    if kwargs.get('mark_read', False):
        notification.mark_as_read()
    if kwargs.get('delete', False):
        notification.delete()
    if kwargs.get('refresh', False):
        notification.refresh_from_db()
    return Notification.objects.first()


@database_sync_to_async
def create_object_notification(admin_user):
    obj = IgnoreObjectNotification.objects.create(
        object_id=admin_user.pk,
        object_content_type_id=ContentType.objects.get_for_model(
            admin_user._meta.model
        ).pk,
        user_id=admin_user.pk,
        valid_till=TEST_DATETIME,
    )
    return obj


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestNotificationSockets:
    application = import_string(getattr(settings, 'ASGI_APPLICATION'))

    async def _get_communicator(self, admin_client):
        session_id = admin_client.cookies['sessionid'].value
        communicator = WebsocketCommunicator(
            self.application,
            path='ws/notification/',
            headers=[
                (
                    b'cookie',
                    f'sessionid={session_id}'.encode('ascii'),
                )
            ],
        )
        connected, subprotocol = await communicator.connect()
        assert connected is True
        return communicator

    async def test_new_notification_created(self, admin_user, admin_client):
        communicator = await self._get_communicator(admin_client)
        n = await create_notification(admin_user)
        response = await communicator.receive_json_from()
        response = await communicator.receive_json_from()
        expected_response = {
            'type': 'notification',
            'notification_count': 1,
            'reload_widget': True,
            'notification': NotificationListSerializer(n).data,
        }
        assert response == expected_response
        await communicator.disconnect()

    async def test_read_notification(self, admin_user, admin_client):
        n = await create_notification(admin_user)
        communicator = await self._get_communicator(admin_client)
        await notification_operation(n, mark_read=True)
        response = await communicator.receive_json_from(timeout=2)
        expected_response = {
            'type': 'notification',
            'notification_count': 0,
            'reload_widget': False,
            'notification': None,
        }
        assert response == expected_response
        await communicator.disconnect()

    async def test_delete_notification(self, admin_user, admin_client):
        n = await create_notification(admin_user)
        communicator = await self._get_communicator(admin_client)
        await notification_operation(n, delete=True)
        response = await communicator.receive_json_from()
        expected_response = {
            'type': 'notification',
            'notification_count': 0,
            'reload_widget': True,
            'notification': None,
        }
        assert response == expected_response
        await communicator.disconnect()

    async def test_unauthenticated_user(self, client):
        client.cookies['sessionid'] = 'random'
        with pytest.raises(AssertionError):
            await self._get_communicator(client)

    async def test_receive_notification_data(self, admin_user, admin_client):
        communicator = await self._get_communicator(admin_client)
        n = await create_notification(admin_user)
        # Assert message for new notification created
        await communicator.receive_json_from()
        res = await communicator.receive_json_from()
        assert res['notification_count'] == 1
        await communicator.send_json_to(
            {'type': 'notification', 'notification_id': str(n.id)}
        )
        # Assert message for notification mark read
        res = await communicator.receive_json_from()
        assert res['notification_count'] == 0
        assert await communicator.receive_nothing() is True
        await communicator.disconnect()

    async def test_receive_with_improper_data(self, admin_user, admin_client):
        communicator = await self._get_communicator(admin_client)
        # Check for JSONDecodeError
        await communicator.send_to('Not JSON')
        assert await communicator.receive_nothing() is True

        await communicator.send_json_to(
            {'type': 'notification', 'notification': 'random'}
        )
        assert await communicator.receive_nothing() is True

        await communicator.send_json_to(
            {'type': 'notification', 'notification_id': str(uuid.uuid4())}
        )
        assert await communicator.receive_nothing() is True

    async def test_retreive_object_notification_valid_till(
        self, admin_user, admin_client
    ):
        communicator = await self._get_communicator(admin_client)
        # Test for non-existing object
        payload = {
            'type': 'object_notification',
            'app_label': admin_user._meta.app_label,
            'model_name': admin_user._meta.model_name,
            'object_id': str(admin_user.pk),
        }
        await communicator.send_json_to(payload)
        assert await communicator.receive_nothing() is True

        # Test for an existing object
        with patch('openwisp_notifications.tasks.delete_ignore_object_notification'):
            await create_object_notification(admin_user)
            await communicator.send_json_to(payload)
            response = await communicator.receive_json_from()
            assert response['type'] == 'object_notification'
            assert response['valid_till'].split('T')[0] in TEST_DATETIME.isoformat()
