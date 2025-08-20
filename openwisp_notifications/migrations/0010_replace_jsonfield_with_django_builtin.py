# Generated migration to replace third-party JSONField with Django's built-in JSONField

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openwisp_notifications', '0009_alter_notificationsetting_organization_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='data',
            field=models.JSONField(blank=True, null=True, verbose_name='data'),
        ),
    ]
