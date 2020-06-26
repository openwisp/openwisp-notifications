from django.core.management.base import BaseCommand
from openwisp_notifications.signals import notify

from openwisp_users.models import Organization


class BaseCreateNotificationCommand(BaseCommand):
    def handle(self, *args, **kwargs):
        default_org = Organization.objects.first()
        notify.send(sender=default_org, type='default')
