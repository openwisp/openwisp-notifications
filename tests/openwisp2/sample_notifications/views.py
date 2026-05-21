"""
You don't need to have this file unless you plan to modify the API views as well.
"""

from openwisp_notifications.api.views import (
    IgnoreObjectNotificationListView as BaseIgnoreObjectNotificationListView,
)
from openwisp_notifications.api.views import (
    IgnoreObjectNotificationView as BaseIgnoreObjectNotificationView,
)
from openwisp_notifications.api.views import (
    NotificationDetailView as BaseNotificationDetailView,
)
from openwisp_notifications.api.views import (
    NotificationListView as BaseNotificationListView,
)
from openwisp_notifications.api.views import (
    NotificationReadAllView as BaseNotificationReadAllView,
)
from openwisp_notifications.api.views import (
    NotificationReadRedirect as BaseNotificationReadRedirect,
)
from openwisp_notifications.api.views import (
    NotificationSettingListView as BaseNotificationSettingListView,
)
from openwisp_notifications.api.views import (
    NotificationSettingView as BaseNotificationSettingView,
)
from openwisp_notifications.api.views import (
    OrganizationNotificationSettingView as BaseOrganizationNotificationSettingView,
)
from openwisp_notifications.api.views import (
    UserOrgNotificationSettingView as BaseUserOrgNotificationSettingView,
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


class NotificationReadRedirect(BaseNotificationReadRedirect):
    pass


class NotificationSettingView(BaseNotificationSettingView):
    """
    Retrives details for a notification setting and provides
    endpoints for updating and deleting them.
    """

    pass


class NotificationSettingListView(BaseNotificationSettingListView):
    """
    Lists user's notification settings.
    """

    pass


class UserOrgNotificationSettingView(BaseUserOrgNotificationSettingView):
    pass


class IgnoreObjectNotificationView(BaseIgnoreObjectNotificationView):
    """
    Retrives details for a IgnoreNotificationObject object and
    provides endpoints for updating and deleting it.
    """

    pass


class IgnoreObjectNotificationListView(BaseIgnoreObjectNotificationListView):
    """
    Lists user's IgnoreObjectNotification objects.
    """

    pass


class OrganizationNotificationSettingView(BaseOrganizationNotificationSettingView):
    """
    Retrives details for a organization notification setting and
    provides endpoints for updating and deleting it.
    """

    pass


notifications_list = NotificationListView.as_view()
notification_detail = NotificationDetailView.as_view()
notifications_read_all = NotificationReadAllView.as_view()
notification_read_redirect = NotificationReadRedirect.as_view()
notification_setting_list = NotificationSettingListView.as_view()
notification_setting = NotificationSettingView.as_view()
user_org_notification_setting = UserOrgNotificationSettingView.as_view()
org_notification_setting = OrganizationNotificationSettingView.as_view()
ignore_object_notification_list = IgnoreObjectNotificationListView.as_view()
ignore_object_notification = IgnoreObjectNotificationView.as_view()
