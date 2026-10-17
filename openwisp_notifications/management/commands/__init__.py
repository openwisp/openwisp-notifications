from django.core.management.base import BaseCommand

from openwisp_notifications.handlers import (
    notification_type_registered_unregistered_handler,
)
from openwisp_notifications.signals import notify
from openwisp_notifications.swapper import swapper_load_model

Organization = swapper_load_model("openwisp_users", "Organization")


class BaseCreateNotificationCommand(BaseCommand):
    def handle(self, *args, **kwargs):
        default_org = Organization.objects.first()
        default_org.organization_id = default_org.id
        results = notify.send(
            sender=default_org, type="generic_message", target=default_org
        )
        for _, notifications in results:
            for notification in notifications:
                recipient = notification.recipient
                if recipient.emailaddress_set.filter(
                    verified=True, email=recipient.email
                ).exists():
                    notification.send_email()


class BasePopulateNotificationPreferencesCommand(BaseCommand):
    def handle(self, *args, **kwargs):
        notification_type_registered_unregistered_handler(self)
