import logging

from django.db import models
from openwisp_notifications.exceptions import NotificationRenderException
from openwisp_notifications.swapper import load_model
from openwisp_notifications.utils import _get_object_link
from rest_framework import serializers
from rest_framework.exceptions import NotFound

logger = logging.getLogger(__name__)

Notification = load_model('Notification')


class ContentTypeField(serializers.Field):
    def to_representation(self, obj):
        return obj.model


class CustomListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        iterable = data.all() if isinstance(data, models.Manager) else data
        data_list = []
        for item in iterable:
            try:
                data_list.append(self.child.to_representation(item))
            except NotificationRenderException as e:
                logger.error(e)
        return data_list


class NotificationSerializer(serializers.ModelSerializer):
    target_object_url = serializers.SerializerMethodField()
    actor_content_type = ContentTypeField(read_only=True)
    target_content_type = ContentTypeField(read_only=True)
    action_object_content_type = ContentTypeField(read_only=True)

    class Meta:
        model = Notification
        exclude = ['description', 'deleted', 'public']
        extra_fields = ['message', 'email_subject', 'target_object_url']

    def get_field_names(self, declared_fields, info):
        model_fields = super().get_field_names(declared_fields, info)
        return model_fields + self.Meta.extra_fields

    def get_target_object_url(self, obj):
        return _get_object_link(obj, 'target', url_only=True, absolute_url=True)

    @property
    def data(self):
        try:
            return super().data
        except NotificationRenderException as e:
            logger.error(e)
            raise NotFound


class NotificationListSerializer(NotificationSerializer):
    class Meta(NotificationSerializer.Meta):
        fields = [
            'id',
            'message',
            'unread',
            'target_object_url',
            'email_subject',
            'timestamp',
            'level',
        ]
        exclude = None
        list_serializer_class = CustomListSerializer
