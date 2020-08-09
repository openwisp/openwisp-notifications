from openwisp_notifications.apps import OpenwispNotificationsConfig
from openwisp_notifications.types import register_notification_type


class SampleNotificationsConfig(OpenwispNotificationsConfig):
    name = 'openwisp2.sample_notifications'
    label = 'sample_notifications'
    verbose_name = 'Notifications (custom)'

    def ready(self):
        super().ready()
        self.register_notification_types()

    def register_notification_types(self):
        register_notification_type(
            'object_created',
            {
                'verbose_name': 'Object created',
                'verb': 'created',
                'level': 'info',
                'message': '{notification.target} object {notification.verb}.',
                'email_subject': '[{site.name}] INFO: {notification.target} created',
            },
        )
