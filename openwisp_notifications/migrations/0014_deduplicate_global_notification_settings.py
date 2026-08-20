from django.db import migrations, models


def merge_global_notification_settings(settings):
    """
    Merge duplicate global notification settings into a single set of values.

    Resolution rules:
      - Explicit ``False`` wins over ``True`` and ``None`` for both web and email.
      - ``True`` wins over ``None``.
      - If any row is active (deleted=False), the merged row stays active.
    """
    merged = {"web": None, "email": None, "deleted": True}
    for setting in settings:
        for field in ("web", "email"):
            value = getattr(setting, field)
            current = merged[field]
            if value is False:
                merged[field] = False
            elif value is True and current is not False:
                merged[field] = True
        if not getattr(setting, "deleted", False):
            merged["deleted"] = False
    return merged


def deduplicate_global_notification_settings(apps, schema_editor):
    NotificationSetting = apps.get_model(
        "openwisp_notifications", "NotificationSetting"
    )
    duplicate_users = (
        NotificationSetting.objects.filter(organization__isnull=True, type__isnull=True)
        .values("user")
        .annotate(count=models.Count("id"))
        .filter(count__gt=1)
    )
    for duplicate in duplicate_users.iterator():
        user_id = duplicate["user"]
        settings = list(
            NotificationSetting.objects.filter(
                user_id=user_id, organization__isnull=True, type__isnull=True
            ).order_by("pk")
        )
        if len(settings) < 2:
            continue
        keep = settings[0]
        merged = merge_global_notification_settings(settings)
        NotificationSetting.objects.filter(pk=keep.pk).update(
            web=merged["web"],
            email=merged["email"],
            deleted=merged["deleted"],
        )
        NotificationSetting.objects.filter(
            pk__in=[setting.pk for setting in settings[1:]]
        ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("openwisp_notifications", "0013_make_notification_type_nonnullable"),
    ]
    operations = [
        migrations.RunPython(
            deduplicate_global_notification_settings,
            reverse_code=migrations.RunPython.noop,
        )
    ]
