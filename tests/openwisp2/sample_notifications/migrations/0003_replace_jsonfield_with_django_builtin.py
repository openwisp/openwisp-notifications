# Generated migration to replace third-party JSONField with Django's built-in JSONField

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sample_notifications', '0002_testapp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='data',
            field=models.JSONField(blank=True, null=True, verbose_name='data'),
        ),
    ]
