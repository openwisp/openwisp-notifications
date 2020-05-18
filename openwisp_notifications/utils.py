from django.contrib.sites.models import Site
from django.urls import NoReverseMatch, reverse
from django.utils.html import format_html


def _get_object_link(obj, field, html=True, url_only=False, absolute_url=False):
    site = Site.objects.get_current()
    content_type = getattr(obj, f'{field}_content_type', None)
    object_id = getattr(obj, f'{field}_object_id', None)
    try:
        url = reverse(
            f'admin:{content_type.app_label}_{content_type.model}_change',
            args=[object_id],
        )
        if absolute_url:
            url = f'http://{site.domain}{url}'
        if not html:
            return url
        return format_html(f'<a href="{url}" id="{field}-object-url">{object_id}</a>')
    except NoReverseMatch:
        fallback_content = object_id
    except AttributeError:
        fallback_content = '-'
    if url_only:
        return '#'
    return fallback_content
