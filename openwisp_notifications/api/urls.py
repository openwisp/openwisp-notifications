from django.urls import path

from openwisp_notifications.api import views

app_name = 'openwisp_notifications'


def get_api_urls(api_views=None):
    if not api_views:
        api_views = views
    return [
        path('', views.notifications_list, name='notifications_list'),
        path('read/', views.notifications_read_all, name='notifications_read_all'),
        path('<uuid:pk>/', views.notification_detail, name='notification_detail'),
        path(
            '<uuid:pk>/redirect/',
            views.notification_read_redirect,
            name='notification_read_redirect',
        ),
    ]
