from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class OpenwispNotificationsConfig(AppConfig):
    name = 'openwisp_notifications'
    label = 'openwisp_notifications'
    verbose_name = _('Notifications')

    def ready(self):
        from openwisp_notifications.handlers import notify_handler
        from openwisp_notifications.signals import notify

        notify.connect(
            notify_handler, dispatch_uid='openwisp_notifications.model.notifications'
        )

        # Add CORS configuration checks
        from openwisp_notifications.checks import check_cors_configuration  # noqa
