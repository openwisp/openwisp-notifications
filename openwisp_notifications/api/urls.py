from django.urls import path

from openwisp_notifications.api import views

app_name = "openwisp_notifications"


def get_api_urls(api_views=None):
    if not api_views:
        api_views = views

    def get_api_view(name):
        return getattr(api_views, name, getattr(views, name))

    return [
        path(
            "notification/",
            get_api_view("notifications_list"),
            name="notifications_list",
        ),
        path(
            "notification/read/",
            get_api_view("notifications_read_all"),
            name="notifications_read_all",
        ),
        path(
            "notification/<uuid:pk>/",
            get_api_view("notification_detail"),
            name="notification_detail",
        ),
        path(
            "notification/<uuid:pk>/redirect/",
            get_api_view("notification_read_redirect"),
            name="notification_read_redirect",
        ),
        path(
            "user/<uuid:user_id>/user-setting/",
            get_api_view("notification_setting_list"),
            name="user_notification_setting_list",
        ),
        path(
            "user/<uuid:user_id>/user-setting/<uuid:pk>/",
            get_api_view("notification_setting"),
            name="user_notification_setting",
        ),
        path(
            "user/<uuid:user_id>/organization/<uuid:organization_id>/setting/",
            get_api_view("user_org_notification_setting"),
            name="user_org_notification_setting",
        ),
        path(
            "notification/ignore/",
            get_api_view("ignore_object_notification_list"),
            name="ignore_object_notification_list",
        ),
        path(
            "notification/ignore/<str:app_label>/<str:model_name>/<uuid:object_id>/",
            get_api_view("ignore_object_notification"),
            name="ignore_object_notification",
        ),
        path(
            "organization/<uuid:organization_id>/setting/",
            get_api_view("org_notification_setting"),
            name="org_notification_setting",
        ),
        # DEPRECATED
        path(
            "user/user-setting/",
            get_api_view("notification_setting_list"),
            name="notification_setting_list",
        ),
        path(
            "user/user-setting/<uuid:pk>/",
            get_api_view("notification_setting"),
            name="notification_setting",
        ),
    ]
