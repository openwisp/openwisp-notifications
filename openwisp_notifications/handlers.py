from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.db.models.query import QuerySet
from django.utils import timezone
from openwisp_notifications import settings as app_settings
from swapper import load_model

User = get_user_model()

EXTRA_DATA = app_settings.get_config()['USE_JSONFIELD']

Notification = load_model('openwisp_notifications', 'Notification')


def notify_handler(verb, **kwargs):
    """
    Handler function to create Notification instance upon action signal call.
    """
    # Pull the options out of kwargs
    kwargs.pop('signal', None)
    actor = kwargs.pop('sender')
    public = bool(kwargs.pop('public', True))
    description = kwargs.pop('description', None)
    timestamp = kwargs.pop('timestamp', timezone.now())
    level = kwargs.pop('level', Notification.LEVELS.info)
    recipient = kwargs.pop('recipient', None)

    target_org = getattr(kwargs.get('target', None), 'organization_id', None)

    where = Q(is_superuser=True)
    where_group = Q()
    if target_org:
        where = where | (Q(is_staff=True) & Q(openwisp_users_organization=target_org))
        where_group = Q(openwisp_users_organization=target_org)
    where_group = where_group & Q(notificationuser__receive=True)
    where = where & Q(notificationuser__receive=True)

    if recipient:
        # Check if recipient is User, Group or QuerySet
        if isinstance(recipient, Group):
            recipients = recipient.user_set.filter(where_group)
        elif isinstance(recipient, (QuerySet, list)):
            recipients = recipient
        else:
            recipients = [recipient]
    else:
        recipients = (
            User.objects.select_related('notificationuser')
            .order_by('date_joined')
            .filter(where)
        )
    new_notifications = []

    optional_objs = [
        (kwargs.pop(opt, None), opt) for opt in ('target', 'action_object')
    ]

    for recipient in recipients:
        newnotify = Notification(
            recipient=recipient,
            actor_content_type=ContentType.objects.get_for_model(actor),
            actor_object_id=actor.pk,
            verb=str(verb),
            public=public,
            description=description,
            timestamp=timestamp,
            level=level,
        )

        # Set optional objects
        for obj, opt in optional_objs:
            if obj is not None:
                setattr(newnotify, '%s_object_id' % opt, obj.pk)
                setattr(
                    newnotify,
                    '%s_content_type' % opt,
                    ContentType.objects.get_for_model(obj),
                )
        if kwargs and EXTRA_DATA:
            newnotify.data = kwargs
        newnotify.save()
        new_notifications.append(newnotify)

    return new_notifications
