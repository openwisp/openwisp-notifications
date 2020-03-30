from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class OpenwispNotificationsConfig(AppConfig):
    name = 'openwisp_notifications'
    verbose_name = _('Openwisp Notifications')
