from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'openwisp2.settings')

app = Celery('openwisp2')
app.config_from_object('django.conf:settings', namespace='CELERY')
"""
Delete notifications having 'timestamp' more than 90 days, task scheduled for every Monday 2:00 a.m.
"""
app.conf.beat_schedule = {
    'delete-expired-notifications-every-monday': {
        'task': 'openwisp_notifications.tasks.delete_expired_notifications',
        'schedule': crontab(hour=2, day_of_week=1),
        'args': (90,)
    },
}
app.conf.timezone = 'UTC'
app.autodiscover_tasks()
