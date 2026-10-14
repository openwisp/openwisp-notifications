from django.apps import AppConfig

from openwisp_notifications.types import register_notification_type


class DefaultTypeConfig(AppConfig):
    name = "openwisp2.default_type"
    label = "default_type"

    def ready(self):
        register_notification_type(
            "default",
            {
                "level": "info",
                "verb": "default verb",
                "verbose_name": "Default Type",
                "email_subject": "[{site.name}] Default Notification Subject",
                "message": (
                    "Default notification with {notification.verb}"
                    " and level {notification.level}"
                    " by [{notification.target}]({notification.target_link})"
                ),
                "message_template": "openwisp_notifications/default_message.md",
                "email_notification": True,
                "web_notification": True,
            },
        )
