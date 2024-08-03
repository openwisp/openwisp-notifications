from django.urls import include, path

from .api.urls import get_api_urls
from .base.views import notifiation_setting_page


def get_urls(api_views=None, social_views=None):
    """
    Returns a list of urlpatterns
    Arguments:
        api_views(optional): views for Notifications API
    """
    urls = [
        path('api/v1/notifications/', include(get_api_urls(api_views))),
        path(
            'notifications/settings/',
            notifiation_setting_page,
            name='notifications_settings',
        ),
        path(
            'notifications/user/<uuid:pk>/settings/',
            notifiation_setting_page,
            name='user_notification_settings',
        ),
    ]
    return urls


app_name = 'notifications'
urlpatterns = get_urls()
