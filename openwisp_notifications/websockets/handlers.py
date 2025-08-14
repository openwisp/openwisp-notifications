from asgiref.sync import async_to_sync
from channels import layers
from django.core.cache import cache
from django.db.models import Count, Q
from django.utils.timezone import now, timedelta

from openwisp_notifications.utils import normalize_unread_count

from .. import settings as app_settings
from ..swapper import load_model

Notification = load_model("Notification")


def bulk_check_notification_storm_and_unread_count(recipients):
    if not recipients:
        return {}
    recipient_ids = [recipient.pk for recipient in recipients]
    cached_storm_data = cache.get_many([f"ow-noti-storm-{pk}" for pk in recipient_ids])
    results = {}
    uncached_recipients = []
    for recipient in recipients:
        cache_key = f"ow-noti-storm-{recipient.pk}"
        if cache_key in cached_storm_data:
            results[recipient.pk] = [cached_storm_data[cache_key], None]
        else:
            uncached_recipients.append(recipient)
            results[recipient.pk] = [False, None]
    if uncached_recipients:
        short_term_threshold = now() - timedelta(
            seconds=app_settings.NOTIFICATION_STORM_PREVENTION["short_term_time_period"]
        )
        long_term_threshold = now() - timedelta(
            seconds=app_settings.NOTIFICATION_STORM_PREVENTION["long_term_time_period"]
        )
        uncached_recipient_ids = [recipient.pk for recipient in uncached_recipients]
        storm_and_unread_data = list(
            Notification.objects.filter(recipient_id__in=uncached_recipient_ids)
            .values("recipient_id")
            .annotate(
                short_term_count=Count(
                    "id", filter=Q(timestamp__gte=short_term_threshold)
                ),
                long_term_count=Count(
                    "id", filter=Q(timestamp__gte=long_term_threshold)
                ),
                unread_count=Count("id", filter=Q(unread=True)),
            )
        )
        cache_updates = {}
        for data in storm_and_unread_data:
            recipient_id = data["recipient_id"]
            in_storm = (
                data["short_term_count"]
                > app_settings.NOTIFICATION_STORM_PREVENTION[
                    "short_term_notification_count"
                ]
                or data["long_term_count"]
                > app_settings.NOTIFICATION_STORM_PREVENTION[
                    "long_term_notification_count"
                ]
            )
            results[recipient_id] = [in_storm, data["unread_count"]]
            if in_storm:
                cache_updates[f"ow-noti-storm-{recipient_id}"] = True
        if cache_updates:
            cache.set_many(cache_updates, timeout=60)
        fetched_recipient_ids = {data["recipient_id"] for data in storm_and_unread_data}
        for recipient in uncached_recipients:
            if recipient.pk not in fetched_recipient_ids:
                results[recipient.pk] = [False, 0]
    if any(results[pk][1] is None for pk in results):
        recipients_needing_unread = [pk for pk in results if results[pk][1] is None]
        unread_data = (
            Notification.objects.filter(
                recipient_id__in=recipients_needing_unread, unread=True
            )
            .values("recipient_id")
            .annotate(unread_count=Count("id"))
        )
        for data in unread_data:
            results[data["recipient_id"]][1] = data["unread_count"]
        for pk in recipients_needing_unread:
            if results[pk][1] is None:
                results[pk][1] = 0
    return {pk: (storm, unread) for pk, (storm, unread) in results.items()}


def user_in_notification_storm(user):
    """
    A user is affected by notifications storm if any of short term
    or long term check passes. The checks are configured by
    "OPENWISP_NOTIFICATIONS_NOTIFICATION_STORM_PREVENTION" setting.
    If the user is found to be affected by a notification storm,
    the value of this function is cached for 60 seconds.
    """
    in_notification_storm = cache.get(f"ow-noti-storm-{user.pk}", False)
    if in_notification_storm:
        return True
    if (
        user.notifications.filter(
            timestamp__gte=now()
            - timedelta(
                seconds=app_settings.NOTIFICATION_STORM_PREVENTION[
                    "short_term_time_period"
                ]
            )
        ).count()
        > app_settings.NOTIFICATION_STORM_PREVENTION["short_term_notification_count"]
    ):
        in_notification_storm = True
    elif (
        user.notifications.filter(
            timestamp__gte=now()
            - timedelta(
                seconds=app_settings.NOTIFICATION_STORM_PREVENTION[
                    "long_term_time_period"
                ]
            )
        ).count()
        > app_settings.NOTIFICATION_STORM_PREVENTION["long_term_notification_count"]
    ):
        in_notification_storm = True
    if in_notification_storm:
        cache.set(f"ow-noti-storm-{user.pk}", True, 60)
    return in_notification_storm


def bulk_notification_update_handler(
    recipients, reload_widget=False, notification_map=None
):
    if not recipients:
        return
    channel_layer = layers.get_channel_layer()
    bulk_data = bulk_check_notification_storm_and_unread_count(recipients)
    for recipient in recipients:
        in_storm, unread_count = bulk_data.get(recipient.pk, (False, 0))
        serialized_notification = None
        if notification_map and recipient in notification_map:
            from openwisp_notifications.api.serializers import (
                NotificationListSerializer,
            )

            try:
                serialized_notification = NotificationListSerializer(
                    notification_map[recipient]
                ).data
            except Exception:
                pass
        async_to_sync(channel_layer.group_send)(
            f"ow-notification-{recipient.pk}",
            {
                "type": "send.updates",
                "reload_widget": reload_widget,
                "notification": serialized_notification,
                "recipient": str(recipient.pk),
                "in_notification_storm": in_storm,
                "notification_count": normalize_unread_count(unread_count),
            },
        )


def notification_update_handler(reload_widget=False, notification=None, recipient=None):
    if recipient is None:
        return
    notification_map = {recipient: notification} if notification else None
    bulk_notification_update_handler([recipient], reload_widget, notification_map)
