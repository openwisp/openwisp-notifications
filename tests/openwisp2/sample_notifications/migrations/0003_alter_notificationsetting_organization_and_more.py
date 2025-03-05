# Generated by Django 4.2.16 on 2024-09-17 13:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("openwisp_users", "0020_populate_password_updated_field"),
        ("sample_notifications", "0002_testapp"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notificationsetting",
            name="organization",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="openwisp_users.organization",
            ),
        ),
        migrations.AlterField(
            model_name="notificationsetting",
            name="type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("default", "Default Type"),
                    ("generic_message", "Generic Message Type"),
                    ("object_created", "Object created"),
                ],
                max_length=30,
                null=True,
                verbose_name="Notification Type",
            ),
        ),
    ]
