# chat/routing.py
from django.urls import re_path

from . import consumers as ow_consumers


def get_routes(consumer=None):
    if not consumer:
        consumer = ow_consumers
    return [
        re_path(r'ws/notification/$', consumer.NotificationConsumer.as_asgi()),
    ]
