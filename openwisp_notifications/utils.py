from django.conf import settings
from django.contrib.sites.models import Site
from django.urls import NoReverseMatch, reverse


def _get_object_link(obj, field, url_only=False, absolute_url=False, *args, **kwargs):
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


def _get_absolute_url(url):
    site = Site.objects.get_current()
    protocol = 'http' if getattr(settings, 'DEBUG', False) else 'https'
    return f'{protocol}://{site.domain}{url}'


def normalize_unread_count(unread_count):
    if unread_count > 99:
        return '99+'
    else:
        return unread_count
