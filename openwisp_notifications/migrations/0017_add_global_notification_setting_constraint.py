from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "openwisp_notifications",
            "0016_populate_global_notification_setting_marker",
        ),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="notificationsetting",
            constraint=models.UniqueConstraint(
                fields=("user", "_global"),
                name="unique_global_notification_setting",
            ),
        ),
    ]
