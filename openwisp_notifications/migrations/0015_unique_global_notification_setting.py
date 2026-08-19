from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "openwisp_notifications",
            "0014_deduplicate_global_notification_settings",
        ),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="notificationsetting",
            constraint=models.UniqueConstraint(
                fields=("user",),
                condition=models.Q(organization__isnull=True, type__isnull=True),
                name="unique_global_notification_setting",
            ),
        ),
    ]
