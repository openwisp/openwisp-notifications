from django.conf import settings
from notifications.settings import CONFIG_DEFAULTS

CONFIG_DEFAULTS.update({'USE_JSONFIELD': True})

OPENWISP_NOTIFICATION_EMAIL_TEMPLATE = getattr(
    settings,
    'OPENWISP_NOTIFICATION_EMAIL_TEMPLATE',
    'openwisp_notifications/email_template.html',
)

OPENWISP_NOTIFICATION_EMAIL_LOGO = getattr(
    settings,
    'OPENWISP_NOTIFICATION_EMAIL_LOGO',
    'https://raw.githubusercontent.com/openwisp/openwisp-notifications/master/openwisp_notifications/'
    'static/openwisp_notifications/images/openwisp-logo.png',
)

OPENWISP_NOTIFICATION_HTML_EMAIL = getattr(
    settings, 'OPENWISP_NOTIFICATION_HTML_EMAIL', True
)


def get_config():
    user_config = getattr(settings, 'OPENWISP_NOTIFICATIONS_CONFIG', {})
    config = CONFIG_DEFAULTS.copy()
    config.update(user_config)
    return config
