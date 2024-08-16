from django.urls import include, path

from .api.urls import get_api_urls
from .base.views import notifiation_preference_page


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
            notifiation_preference_page,
            name='notification_preferences',
        ),
        path(
            'notifications/user/<uuid:pk>/preferences/',
            notifiation_preference_page,
            name='user_notification_preferences',
        ),
    ]
    return urls


app_name = 'notifications'
urlpatterns = get_urls()
