from django.db import migrations, models

from openwisp_notifications.types import get_notification_choices


class Migration(migrations.Migration):
    dependencies = [
        ("openwisp_notifications", "0002_default_permissions"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="type",
            field=models.CharField(
                choices=get_notification_choices,
                max_length=30,
                null=True,
                verbose_name="Notification Type",
            ),
        ),
    ]
