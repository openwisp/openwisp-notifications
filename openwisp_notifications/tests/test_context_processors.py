from types import SimpleNamespace
from unittest.mock import patch

from django.templatetags.static import static
from django.test import RequestFactory, SimpleTestCase

from openwisp_notifications import settings as app_settings
from openwisp_notifications.context_processors import notification_widget_settings


class NotificationContextProcessorTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch.object(app_settings, "NOTIFICATION_WIDGET_ENABLE", False)
    def test_widget_disabled_by_global_setting(self):
        request = self.factory.get("/")
        request.user = SimpleNamespace(is_authenticated=True)
        request.resolver_match = SimpleNamespace(namespace="admin")
        context = notification_widget_settings(request)
        self.assertFalse(context["show_notifications_widget"])
        self.assertNotIn("OPENWISP_NOTIFICATIONS_HOST", context)
        self.assertNotIn("OPENWISP_NOTIFICATIONS_SOUND", context)

    @patch.object(app_settings, "HOST", "http://api.example.com")
    @patch.object(app_settings, "SOUND", "sound/file.mp3")
    def test_widget_enabled_by_namespace_and_user_authenticated(self):
        request = self.factory.get("/")
        request.user = SimpleNamespace(is_authenticated=True)
        request.resolver_match = SimpleNamespace(namespace="admin")
        context = notification_widget_settings(request)
        self.assertTrue(context["show_notifications_widget"])
        self.assertEqual(
            context["OPENWISP_NOTIFICATIONS_HOST"], "http://api.example.com"
        )
        self.assertEqual(
            context["OPENWISP_NOTIFICATIONS_SOUND"], static("sound/file.mp3")
        )

    def test_widget_disabled_when_not_authenticated(self):
        request = self.factory.get("/")
        request.user = SimpleNamespace(is_authenticated=False)
        request.resolver_match = SimpleNamespace(namespace="admin")
        context = notification_widget_settings(request)
        self.assertFalse(context["show_notifications_widget"])
        self.assertNotIn("OPENWISP_NOTIFICATIONS_HOST", context)
        self.assertNotIn("OPENWISP_NOTIFICATIONS_SOUND", context)

    def test_widget_disabled_by_namespace_not_allowed(self):
        request = self.factory.get("/")
        request.user = SimpleNamespace(is_authenticated=True)
        request.resolver_match = SimpleNamespace(namespace="unknown")
        context = notification_widget_settings(request)
        self.assertFalse(context["show_notifications_widget"])
        self.assertNotIn("OPENWISP_NOTIFICATIONS_HOST", context)
        self.assertNotIn("OPENWISP_NOTIFICATIONS_SOUND", context)
