from django.conf import settings
from notifications.settings import CONFIG_DEFAULTS

CONFIG_DEFAULTS.update({'USE_JSONFIELD': True})

OPENWISP_NOTIFICATIONS_HOST = getattr(settings, 'OPENWISP_NOTIFICATIONS_HOST', None)
OPENWISP_NOTIFICATIONS_SOUND = getattr(
    settings,
    'OPENWISP_NOTIFICATIONS_SOUND',
    '/static/openwisp-notifications/audio/notification_bell.mp3',
)

OPENWISP_NOTIFICATIONS_CACHE_TIMEOUT = getattr(
    settings, 'OPENWISP_NOTIFICATIONS_CACHE_TIMEOUT', 2 * 24 * 60 * 60
)

IGNORE_ENABLED_ADMIN = getattr(
    settings, 'OPENWISP_NOTIFICATIONS_IGNORE_ENABLED_ADMIN', []
)
POPULATE_PREFERENCES_ON_MIGRATE = getattr(
    settings, 'OPENWISP_NOTIFICATIONS_POPULATE_PREFERENCES_ON_MIGRATE', True
)


def get_config():
    user_config = getattr(settings, 'OPENWISP_NOTIFICATIONS_CONFIG', {})
    config = CONFIG_DEFAULTS.copy()
    config.update(user_config)
    return config
