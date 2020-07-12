from django.contrib.sites.models import Site
from django.urls import NoReverseMatch, reverse


class NotificationException(Exception):
    pass


def _get_object_link(obj, field, url_only=False, absolute_url=False):
    content_type = getattr(obj, f'{field}_content_type', None)
    object_id = getattr(obj, f'{field}_object_id', None)
    try:
        url = reverse(
            f'admin:{content_type.app_label}_{content_type.model}_change',
            args=[object_id],
        )
        if absolute_url:
            url = _get_absolute_url(url)
        return url
    except (NoReverseMatch, AttributeError):
        return '#'


def _get_absolute_url(url):
    site = Site.objects.get_current()
    return f'http://{site.domain}{url}'


def normalize_unread_count(unread_count):
    if unread_count > 99:
        return '99+'
    else:
        return unread_count
