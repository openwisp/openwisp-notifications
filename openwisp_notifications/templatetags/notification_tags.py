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


def notification_widget():
    return format_html(
        '''
        <div class="ow-notification-dropdown ow-hide">
            <div class="filters">
                <span class="btn" id="ow-mark-all-read" tabindex="1" role="button">Mark all as read</span>
                <span class="btn" id="ow-show-unread" tabindex="2" role="button">Show unread only</span>
            </div>
            <div class="ow-notification-wrapper ow-round-bottom-border">
                <div id="ow-notifications-loader" class="ow-hide"><div class="loader"></div></div>
            </div>
            <div class="ow-no-notifications ow-round-bottom-border ow-hide">
                <p>No new notification.</p>
            </div>
        </div>
        '''
    )


def notification_toast():
    return format_html('<div class="ow-notification-toast-wrapper"></div>')


register.simple_tag(takes_context=True)(unread_notifications)
register.simple_tag(takes_context=False)(notification_widget)
register.simple_tag(takes_context=False)(notification_toast)
