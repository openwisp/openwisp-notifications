import os

from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('api/v1/', include('openwisp_utils.api.urls')),
    path('api/v1/', include(('openwisp_users.api.urls', 'users'), namespace='users')),
]

if os.environ.get('SAMPLE_APP', False):
    # Load custom api views:
    # This should be done when you are extending the app and modifying the API
    # views in your extended application.
    from openwisp_notifications.urls import get_urls

    from .sample_notifications import views as api_views

    urlpatterns += [
        path(
            '',
            include((get_urls(api_views), 'notifications'), namespace='notifications'),
        )
    ]
else:
    # Load openwisp_notifications api views:
    # This can be used when you are extending the app but not making
    # any changes in the API views.
    urlpatterns += [
        path('', include('openwisp_notifications.urls', namespace='notifications'))
    ]

urlpatterns += staticfiles_urlpatterns()
