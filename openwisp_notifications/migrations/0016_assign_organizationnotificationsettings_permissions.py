from django.db import migrations

from openwisp_notifications.migrations import (
    assign_organizationnotificationsettings_permissions_to_groups,
)


class Migration(migrations.Migration):

    dependencies = [
        ("openwisp_notifications", "0015_unique_global_notification_setting"),
        ("openwisp_users", "0004_default_groups"),
    ]

    operations = [
        migrations.RunPython(
            assign_organizationnotificationsettings_permissions_to_groups,
            reverse_code=migrations.RunPython.noop,
        )
    ]
