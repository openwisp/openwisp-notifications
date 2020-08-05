from django.conf import settings
from notifications.settings import CONFIG_DEFAULTS

CONFIG_DEFAULTS.update({'USE_JSONFIELD': True})

OPENWISP_NOTIFICATIONS_EMAIL_TEMPLATE = getattr(
    settings,
    'OPENWISP_NOTIFICATIONS_EMAIL_TEMPLATE',
    'openwisp_notifications/email_template.html',
)

OPENWISP_NOTIFICATIONS_EMAIL_LOGO = getattr(
    settings,
    'OPENWISP_NOTIFICATIONS_EMAIL_LOGO',
    'https://raw.githubusercontent.com/openwisp/openwisp-notifications/master/openwisp_notifications/'
    'static/openwisp-notifications/images/openwisp-logo.png',
)

OPENWISP_NOTIFICATIONS_HTML_EMAIL = getattr(
    settings, 'OPENWISP_NOTIFICATIONS_HTML_EMAIL', True
)

OPENWISP_NOTIFICATIONS_HOST = getattr(settings, 'OPENWISP_NOTIFICATIONS_HOST', None)
OPENWISP_NOTIFICATIONS_SOUND = getattr(
    settings,
    'OPENWISP_NOTIFICATIONS_SOUND',
    '/static/openwisp-notifications/audio/notification_bell.mp3',
)

OPENWISP_NOTIFICATIONS_CACHE_TIMEOUT = getattr(
    settings, 'OPENWISP_NOTIFICATIONS_CACHE_TIMEOUT', 2 * 24 * 60 * 60
)


def get_config():
    user_config = getattr(settings, 'OPENWISP_NOTIFICATIONS_CONFIG', {})
    config = CONFIG_DEFAULTS.copy()
    config.update(user_config)
    return config
