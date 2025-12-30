# -*- coding: utf-8 -*-
import swapper
from django.core.cache import cache
from django.template import Library
from django.utils.html import format_html

from openwisp_notifications.utils import normalize_unread_count

Notification = swapper.load_model("openwisp_notifications", "Notification")
User = swapper.load_model("openwisp_users", "User")
Organization = swapper.load_model("openwisp_users", "Organization")

register = Library()


def _get_user_unread_count(user):
    return user.notifications.unread().count()


def get_notifications_count(context):
    user_pk = context["user"].is_authenticated and context["user"].pk
    cache_key = Notification.count_cache_key(user_pk)
    count = cache.get(cache_key)
    if count is None:
        count = _get_user_unread_count(context["user"])
        count = normalize_unread_count(count)
        cache.set(cache_key, count)
    return count


@register.simple_tag(takes_context=True)
def unread_notifications(context):
    count = get_notifications_count(context)
    output = ""
    if count:
        output = '<span id="ow-notification-count">{0}</span>'
        output = format_html(output.format(count))
    return output


@register.filter
def should_load_notifications_widget(request):
    if not hasattr(request, "user"):
        return False
    return request.user.is_authenticated and request.path.startswith(
        ("/admin", "/notifications")
    )


@register.simple_tag(takes_context=True)
def can_change_notifications(context):
    """
    Template tag to determine whether the "Notification Preferences" button
    should be rendered in the UI.

    The button is shown if:
    - The user is a superuser, OR
    - The user is viewing their own preferences (matches 'user_id' in context), OR
    - The user is staff AND has the 'change_notificationsetting' permission.

    Returns:
        bool: True if the button should be displayed, False otherwise.
    """
    user = context["request"].user
    return (
        user.is_superuser
        or user.id == context.get("user_id")
        or (
            user.is_staff
            and user.has_perm("openwisp_notifications.change_notificationsetting")
        )
    )
