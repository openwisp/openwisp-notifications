# Generated by Django 3.1.13 on 2021-09-17 11:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("openwisp_notifications", "0006_objectnotification"),
    ]

    operations = [
        migrations.AddField(
            model_name="notificationsetting",
            name="deleted",
            field=models.BooleanField(
                blank=True, default=False, null=True, verbose_name="Delete"
            ),
        ),
    ]
