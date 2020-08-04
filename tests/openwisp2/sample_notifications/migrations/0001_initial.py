# Generated by Django 3.0.5 on 2020-04-14 18:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import jsonfield.fields
import model_utils.fields
import uuid
from openwisp_notifications.types import NOTIFICATION_CHOICES


class Migration(migrations.Migration):

    initial = True

    operations = [
        migrations.CreateModel(
            name='NotificationUser',
            fields=[
                (
                    'id',
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    'created',
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name='created',
                    ),
                ),
                (
                    'modified',
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name='modified',
                    ),
                ),
                (
                    'receive',
                    models.BooleanField(
                        default=True,
                        help_text='note: non-superadmin users receive notifications only for organizations of which they are member of.',
                        verbose_name='receive notifications',
                    ),
                ),
                (
                    'email',
                    models.BooleanField(
                        null=True,
                        help_text='note: non-superadmin users receive notifications only for organizations of which they are member of.',
                        verbose_name='email notifications',
                    ),
                ),
                (
                    'user',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ('details', models.CharField(blank=True, max_length=64, null=True)),
            ],
            options={
                'verbose_name': 'user notification settings',
                'verbose_name_plural': 'user notification settings',
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                (
                    'level',
                    models.CharField(
                        choices=[
                            ('success', 'success'),
                            ('info', 'info'),
                            ('warning', 'warning'),
                            ('error', 'error'),
                        ],
                        default='info',
                        max_length=20,
                    ),
                ),
                ('unread', models.BooleanField(db_index=True, default=True)),
                ('actor_object_id', models.CharField(max_length=255)),
                ('verb', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                (
                    'target_object_id',
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    'action_object_object_id',
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    'timestamp',
                    models.DateTimeField(
                        db_index=True, default=django.utils.timezone.now
                    ),
                ),
                ('public', models.BooleanField(db_index=True, default=True)),
                ('deleted', models.BooleanField(db_index=True, default=False)),
                ('emailed', models.BooleanField(db_index=True, default=False)),
                ('data', jsonfield.fields.JSONField(blank=True, null=True)),
                (
                    'id',
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    'action_object_content_type',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='notify_action_object',
                        to='contenttypes.ContentType',
                    ),
                ),
                (
                    'actor_content_type',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='notify_actor',
                        to='contenttypes.ContentType',
                    ),
                ),
                (
                    'recipient',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='notifications',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    'target_content_type',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='notify_target',
                        to='contenttypes.ContentType',
                    ),
                ),
                (
                    'type',
                    models.CharField(
                        choices=NOTIFICATION_CHOICES, max_length=30, null=True,
                    ),
                ),
                ('details', models.CharField(blank=True, max_length=64, null=True)),
            ],
            options={
                'ordering': ('-timestamp',),
                'abstract': False,
                'index_together': {('recipient', 'unread')},
            },
        ),
    ]
