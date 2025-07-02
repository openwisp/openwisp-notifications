import json

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.urls import NoReverseMatch, reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext as _

from openwisp_notifications.exceptions import NotificationRenderException
from openwisp_utils.admin_theme.email import send_email

from .tokens import email_token_generator


def _get_object_link(obj, absolute_url=False, *args, **kwargs):
    try:
        url = reverse(
            f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change",
            args=[obj.id],
        )
        if absolute_url:
            url = _get_absolute_url(url)
        return url
    except (NoReverseMatch, AttributeError):
        return "#"


def _get_absolute_url(path):
    site = Site.objects.get_current()
    protocol = "http" if getattr(settings, "DEBUG", False) else "https"
    return f"{protocol}://{site.domain}{path}"


def normalize_unread_count(unread_count):
    if unread_count > 99:
        return "99+"
    else:
        return unread_count


def get_unsubscribe_url_for_user(user, full_url=True):
    token = email_token_generator.make_token(user)
    data = json.dumps({"user_id": str(user.id), "token": token})
    encoded_data = urlsafe_base64_encode(force_bytes(data))
    unsubscribe_path = reverse("notifications:unsubscribe")
    if not full_url:
        return f"{unsubscribe_path}?token={encoded_data}"
    current_site = Site.objects.get_current()
    return f"https://{current_site.domain}{unsubscribe_path}?token={encoded_data}"


def get_unsubscribe_url_email_footer(url):
    return render_to_string(
        "openwisp_notifications/emails/unsubscribe_footer.html",
        {"unsubscribe_url": url},
    )


def send_notification_email(notification):
    """Send a single email notification"""
    try:
        subject = notification.email_subject
    except NotificationRenderException:
        # Do not send email if notification is malformed.
        return
    url = notification.data.get("url", "") if notification.data else None
    description = notification.message
    if url:
        target_url = url
    elif notification.target:
        target_url = notification.redirect_view_url
    else:
        target_url = None
    if target_url:
        description += _("\n\nFor more information see %(target_url)s.") % {
            "target_url": target_url
        }

    unsubscribe_url = get_unsubscribe_url_for_user(notification.recipient)

    send_email(
        subject,
        description,
        notification.email_message,
        recipients=[notification.recipient.email],
        extra_context={
            "call_to_action_url": target_url,
            "call_to_action_text": _("Find out more"),
            "footer": get_unsubscribe_url_email_footer(unsubscribe_url),
        },
        headers={
            "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
            "List-Unsubscribe": f"<{unsubscribe_url}>",
        },
    )


def get_user_email_preference(notification):
    """
    Returns the user's email preference for notifications.
    If the user has no preference set, it defaults to True.
    """
    target_org = getattr(getattr(notification, "target", None), "organization_id", None)
    if not (notification.type and target_org):
        # We can not check email preference if notification type is absent,
        # or if target_org is not present
        # therefore send email anyway.
        return True
    try:
        return notification.recipient.notificationsetting_set.get(
            organization=target_org, type=notification.type
        ).email_notification
    except ObjectDoesNotExist:
        return False
