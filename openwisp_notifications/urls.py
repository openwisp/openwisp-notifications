from django.urls import include, path

from .api.urls import get_api_urls
from . import views
app_name = 'notifications'


def get_urls(api_views=None, social_views=None):
    """
    Returns a list of urlpatterns
    Arguments:
        api_views(optional): views for Notifications API
    """
    urls = [
        path('api/v1/notifications/notification/', include(get_api_urls(api_views))),
        path('resend-verification-email/', views.resend_verification_email, name='resend_verification_email'),
    ]
    return urls


app_name = 'notifications'
urlpatterns = get_urls()
