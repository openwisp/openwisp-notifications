from django.urls import include, path

from .api.urls import get_api_urls
from .base.views import notification_preference_page


def get_urls(api_views=None, social_views=None):
    """
    Returns a list of urlpatterns
    Arguments:
        api_views(optional): views for Notifications API
    """
    urls = [
        path('api/v1/notifications/', include(get_api_urls(api_views))),
        path(
            'notifications/preferences/',
            notification_preference_page,
            name='notification_preference',
        ),
        path(
            'notifications/user/<uuid:pk>/preferences/',
            notification_preference_page,
            name='user_notification_preference',
        ),
    ]
    return urls


app_name = 'notifications'
urlpatterns = get_urls()
