from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class OpenwispNotificationsConfig(AppConfig):
    name = 'openwisp_notifications'
    verbose_name = _('Openwisp Notifications')

    def ready(self):
        from openwisp_notifications.signals import notify_handler, notify  # noqa

        notify.connect(
            notify_handler, dispatch_uid='openwisp_notifications.model.notifications'
        )
