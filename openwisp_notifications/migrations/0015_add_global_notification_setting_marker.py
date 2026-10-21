from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "openwisp_notifications",
            "0014_deduplicate_global_notification_settings",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="notificationsetting",
            name="_global",
            field=models.BooleanField(editable=False, null=True),
        ),
    ]
