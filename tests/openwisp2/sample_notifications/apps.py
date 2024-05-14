from django.db.models.signals import post_save
from swapper import load_model

from openwisp_notifications.apps import OpenwispNotificationsConfig
from openwisp_notifications.types import register_notification_type

from .signals import test_app_name_changed


class SampleNotificationsConfig(OpenwispNotificationsConfig):
    name = 'openwisp2.sample_notifications'
    label = 'sample_notifications'
    verbose_name = 'Notifications (custom)'

    def ready(self):
        super().ready()
        self.register_notification_types()
        self.connect_receivers()

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

    def connect_receivers(self):
        from openwisp_notifications.handlers import register_notification_cache_update

        Organization = load_model('openwisp_users', 'Organization')
        from .models import TestApp

        register_notification_cache_update(
            Organization, post_save, dispatch_uid='organization_post_save_invalidation'
        )
        register_notification_cache_update(
            TestApp,
            test_app_name_changed,
            dispatch_uid='test_app_name_changed_invalidation',
        )


del OpenwispNotificationsConfig
