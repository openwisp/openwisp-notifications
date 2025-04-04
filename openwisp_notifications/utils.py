from django.conf import settings
from django.contrib.sites.models import Site
from django.urls import NoReverseMatch, reverse


def _get_object_link(obj, absolute_url=False, *args, **kwargs):
    try:
        url = reverse(
            f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change',
            args=[obj.id],
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
