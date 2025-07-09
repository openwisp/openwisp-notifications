from django.templatetags.static import static

from openwisp_notifications import settings as app_settings


def notification_widget_settings(request):
    """
    Injects notification widget settings into template context.

    Variables:
      - show_notifications_widget: boolean flag for loading the notification widget.
      - OPENWISP_NOTIFICATIONS_HOST: API endpoint for notifications (if widget is active).
      - OPENWISP_NOTIFICATIONS_SOUND: URL to notification sound static file (if widget is active).
    """
    # Determine whether to show the notifications widget
    enabled = app_settings.NOTIFICATION_WIDGET_ENABLE
    if not enabled:
        show_widget = False
    else:
        try:
            namespace = request.resolver_match.namespace or ""
        except Exception:
            namespace = ""
        allowed_namespaces = app_settings.NOTIFICATION_WIDGET_ALLOWED_NAMESPACES
        show_widget = namespace in allowed_namespaces and getattr(
            request.user, "is_authenticated", False
        )

    context = {"show_notifications_widget": show_widget}

    if show_widget:
        context["OPENWISP_NOTIFICATIONS_HOST"] = app_settings.HOST
        context["OPENWISP_NOTIFICATIONS_SOUND"] = static(app_settings.SOUND)

    return context
