from django.conf import settings
from django.contrib.sites.models import Site
from django.urls import NoReverseMatch, reverse
from django.utils.translation import gettext as _

from openwisp_notifications.exceptions import NotificationRenderException
from openwisp_utils.admin_theme.email import send_email


def _get_object_link(obj, field, absolute_url=False, *args, **kwargs):
    related_obj = getattr(obj, field)
    try:
        url = reverse(
            f'admin:{related_obj._meta.app_label}_{related_obj._meta.model_name}_change',
            args=[related_obj.id],
        )
        if absolute_url:
            url = _get_absolute_url(url)
        return url
    except (NoReverseMatch, AttributeError):
        return '#'


def _get_absolute_url(path):
    site = Site.objects.get_current()
    protocol = 'http' if getattr(settings, 'DEBUG', False) else 'https'
    return f'{protocol}://{site.domain}{path}'


def normalize_unread_count(unread_count):
    if unread_count > 99:
        return '99+'
    else:
        return unread_count


def send_notification_email(notification):
    """Send a single email notification"""
    try:
        subject = notification.email_subject
    except NotificationRenderException:
        # Do not send email if notification is malformed.
        return
    url = notification.data.get('url', '') if notification.data else None
    description = notification.message
    if url:
        target_url = url
    elif notification.target:
        target_url = notification.redirect_view_url
    else:
        target_url = None
    if target_url:
        description += _('\n\nFor more information see %(target_url)s.') % {
            'target_url': target_url
        }
    send_email(
        subject,
        description,
        notification.email_message,
        recipients=[notification.recipient.email],
        extra_context={
            'call_to_action_url': target_url,
            'call_to_action_text': _('Find out more'),
        },
    )
