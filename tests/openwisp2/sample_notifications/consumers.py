"""
You don't need to have this file unless you plan to modify the web socket consumer as well.
"""

from openwisp_notifications.websockets.consumers import (
    NotificationConsumer as BaseNotificationConsumer,
)


class NotificationConsumer(BaseNotificationConsumer):
    """
    Handle notification updates through websockets.
    """

    pass
