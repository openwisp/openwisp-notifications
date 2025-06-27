import re

from django.conf import settings

CONFIG_DEFAULTS = {
    "PAGINATE_BY": 20,
    "USE_JSONFIELD": True,
    "SOFT_DELETE": False,
    "NUM_TO_FETCH": 10,
    "CACHE_TIMEOUT": 2,
}
DISALLOW_PREFERENCES_CHANGE_TYPE = ["generic_message"]

HOST = getattr(settings, "OPENWISP_NOTIFICATIONS_HOST", None)

CACHE_TIMEOUT = getattr(
    settings, "OPENWISP_NOTIFICATIONS_CACHE_TIMEOUT", 2 * 24 * 60 * 60
)

IGNORE_ENABLED_ADMIN = getattr(
    settings, "OPENWISP_NOTIFICATIONS_IGNORE_ENABLED_ADMIN", []
)
POPULATE_PREFERENCES_ON_MIGRATE = getattr(
    settings, "OPENWISP_NOTIFICATIONS_POPULATE_PREFERENCES_ON_MIGRATE", True
)
NOTIFICATION_STORM_PREVENTION = getattr(
    settings,
    "OPENWISP_NOTIFICATIONS_NOTIFICATION_STORM_PREVENTION",
    {
        "short_term_time_period": 10,
        "short_term_notification_count": 6,
        "long_term_time_period": 180,
        "long_term_notification_count": 30,
        "initial_backoff": 1,
        "backoff_increment": 1,
        "max_allowed_backoff": 15,
    },
)

SOUND = getattr(
    settings,
    "OPENWISP_NOTIFICATIONS_SOUND",
    "openwisp-notifications/audio/notification_bell.mp3",
)

EMAIL_BATCH_INTERVAL = getattr(
    settings, "OPENWISP_NOTIFICATIONS_EMAIL_BATCH_INTERVAL", 180 * 60  # 3 hours
)

EMAIL_BATCH_DISPLAY_LIMIT = getattr(
    settings, "OPENWISP_NOTIFICATIONS_EMAIL_BATCH_DISPLAY_LIMIT", 15
)

# Remove the leading "/static/" here as it will
# conflict with the "static()" call in context_processors.py.
# This is done for backward compatibility.
SOUND = re.sub("^/static/", "", SOUND)


def get_config():
    user_config = getattr(settings, "OPENWISP_NOTIFICATIONS_CONFIG", {})
    config = CONFIG_DEFAULTS.copy()
    config.update(user_config)
    return config
