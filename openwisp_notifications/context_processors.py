from openwisp_notifications import settings as app_settings


def notification_api_settings(request):
    return {
        'OPENWISP_NOTIFICATIONS_HOST': app_settings.OPENWISP_NOTIFICATIONS_HOST,
        'OPENWISP_NOTIFICATIONS_SOUND': app_settings.OPENWISP_NOTIFICATIONS_SOUND,
    }
