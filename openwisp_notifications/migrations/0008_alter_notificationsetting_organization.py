# Generated by Django 4.2.11 on 2024-06-18 13:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("openwisp_users", "0020_populate_password_updated_field"),
        ("openwisp_notifications", "0007_notificationsetting_deleted"),
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
    ]
