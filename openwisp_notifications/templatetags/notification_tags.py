# -*- coding: utf-8 -*-
from django.core.cache import cache
from django.template import Library
from django.utils.html import format_html

from openwisp_notifications.swapper import load_model, swapper_load_model
from openwisp_notifications.utils import normalize_unread_count

Notification = load_model("Notification")
OrganizationUser = swapper_load_model("openwisp_users", "OrganizationUser")

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


def unread_notifications(context):
    count = get_notifications_count(context)
    output = ""
    if count:
        output = format_html('<span id="ow-notification-count">{0}</span>', count)
    return output


@register.filter
def should_load_notifications_widget(request):
    if not hasattr(request, "user"):
        return False
    return request.user.is_authenticated and request.path.startswith(
        ("/admin", "/notifications")
    )


@register.simple_tag
def has_notification_setting_permission(user, target_user=None):
    if not user or not user.is_authenticated:
        return False
    NotificationSetting = load_model("NotificationSetting")
    perm = f"{NotificationSetting._meta.app_label}.change_{NotificationSetting._meta.model_name}"
    if not user.has_perm(perm):
        return False
    if user.is_superuser or target_user is None:
        return True
    return OrganizationUser.objects.filter(
        user=target_user,
        organization_id__in=user.organizations_managed,
    ).exists()


register.simple_tag(takes_context=True)(unread_notifications)
