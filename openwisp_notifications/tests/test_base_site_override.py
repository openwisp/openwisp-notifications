from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class TestBaseSiteOverride(TestCase):
    """
    Ensures notification widget and websocket scripts are only loaded
    on admin and notifications pages, not on other pages (e.g., allauth).
    """

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="password",
        )

    def test_admin_page_includes_notification_widget_and_scripts(self):
        self.client.force_login(self.admin)
        # Admin index page
        response = self.client.get(reverse("admin:index"))
        # Notification widget button
        self.assertContains(response, 'id="openwisp_notifications"')
        # ReconnectingWebSocket script
        self.assertContains(
            response,
            "/static/openwisp-notifications/js/vendor/reconnecting-websocket.min.js",
        )
        # Notifications JS
        self.assertContains(
            response, "/static/openwisp-notifications/js/notifications.js"
        )

    def test_notifications_page_includes_notification_widget_and_scripts(self):
        self.client.force_login(self.admin)
        # Notifications preferences page
        url = reverse("notifications:notification_preference")
        response = self.client.get(url)
        # Notification widget button
        self.assertContains(response, 'id="openwisp_notifications"')
        # ReconnectingWebSocket script
        self.assertContains(
            response,
            "/static/openwisp-notifications/js/vendor/reconnecting-websocket.min.js",
        )
        # Notifications JS
        self.assertContains(
            response, "/static/openwisp-notifications/js/notifications.js"
        )

    def test_allauth_pages_exclude_notification_widget_and_scripts(self):
        # allauth login page
        response = self.client.get(reverse("account_login"))
        # Notification widget should not be present
        self.assertNotContains(response, 'id="openwisp_notifications"')
        # Scripts should not be present
        self.assertNotContains(
            response,
            "/static/openwisp-notifications/js/vendor/reconnecting-websocket.min.js",
        )
        self.assertNotContains(
            response, "/static/openwisp-notifications/js/notifications.js"
        )
