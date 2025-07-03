from django.db import migrations

from openwisp_notifications.migrations import (
    assign_organizationnotificationsettings_permissions_to_groups,
    create_organization_notification_settings,
    reverse_create_organization_notification_settings,
)


class Migration(migrations.Migration):

    dependencies = [
        ("sample_notifications", "0002_testapp"),
    ]

    operations = [
        migrations.RunPython(
            assign_organizationnotificationsettings_permissions_to_groups,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RunPython(
            create_organization_notification_settings,
            reverse_code=reverse_create_organization_notification_settings,
        ),
    ]
