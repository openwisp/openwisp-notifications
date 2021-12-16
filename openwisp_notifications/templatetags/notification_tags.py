# -*- coding: utf-8 -*-
from django.core.cache import cache
from django.template import Library
from django.utils.html import format_html
from notifications.templatetags.notifications_tags import (
    notifications_unread as base_notification_unread,
)

from openwisp_notifications.swapper import load_model
from openwisp_notifications.utils import normalize_unread_count

Notification = load_model('Notification')

register = Library()


def get_notifications_count(context):
    user_pk = context['user'].is_authenticated and context['user'].pk
    cache_key = Notification.count_cache_key(user_pk)
    count = cache.get(cache_key)
    if count is None:
        count = base_notification_unread(context)
        count = normalize_unread_count(count)
        cache.set(cache_key, count)
    return count


def unread_notifications(context):
    count = get_notifications_count(context)
    output = ''
    if count:
        output = '<span id="ow-notification-count">{0}</span>'
        output = format_html(output.format(count))
    return output


register.simple_tag(takes_context=True)(unread_notifications)
