from django.db import migrations, models


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
            "0016_populate_global_notification_setting_marker",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="notificationsetting",
            name="_global",
            field=models.BooleanField(editable=False, null=True),
        ),
        migrations.RunPython(
            set_global_marker,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AddConstraint(
            model_name="notificationsetting",
            constraint=models.UniqueConstraint(
                fields=("user", "_global"),
                name="unique_global_notification_setting",
            ),
        ),
    ]
