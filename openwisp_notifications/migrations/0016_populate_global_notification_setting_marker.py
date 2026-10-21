from django.db import migrations


def set_global_marker(apps, schema_editor):
    NotificationSetting = apps.get_model(
        "openwisp_notifications", "NotificationSetting"
    )
    NotificationSetting.objects.filter(
        organization__isnull=True, type__isnull=True
    ).update(_global=True)


class Migration(migrations.Migration):

    dependencies = [
        (
            "openwisp_notifications",
            "0015_add_global_notification_setting_marker",
        ),
    ]

    operations = [
        migrations.RunPython(
            set_global_marker,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
