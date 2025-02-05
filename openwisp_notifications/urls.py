from django.urls import include, path

from .api.urls import get_api_urls
from .views import resend_verification_email, verify_email

app_name = 'openwisp_notifications'
urlpatterns = [
    path("resend-verification-email/", resend_verification_email, name="resend_verification_email"),
    path('verify-email/<uidb64>/<token>/', verify_email, name='verify_email'),
]


def get_urls(api_views=None, social_views=None):
    """
    Returns a list of urlpatterns
    Arguments:
        api_views(optional): views for Notifications API
    """
    urls = [
        path('api/v1/notifications/notification/', include(get_api_urls(api_views)))
    ]
    return urls


app_name = 'notifications'
urlpatterns += get_urls()
