"""
You don't need to have this file unless you plan to modify the API views as well.
"""

from openwisp_notifications.api.views import (
    NotificationDetailView as BaseNotificationDetailView,
)
from openwisp_notifications.api.views import (
    NotificationListView as BaseNotificationListView,
)
from openwisp_notifications.api.views import (
    NotificationReadAllView as BaseNotificationReadAllView,
)


class NotificationListView(BaseNotificationListView):
    """
    Lists user's notifications
    """

    pass


class NotificationDetailView(BaseNotificationDetailView):
    """
    Retrives details for a notification and provides endpoints
    for marking a notification read and delete it.
    """

    pass


class NotificationReadAllView(BaseNotificationReadAllView):
    """
    Marks all notifications as read
    """

    pass
