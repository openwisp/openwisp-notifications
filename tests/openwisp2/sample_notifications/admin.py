# isort:skip_file
from openwisp_notifications.admin import NotificationSettingInline  # noqa


# Used for testing of openwisp-notifications
from django.contrib import admin

from .models import TestApp


@admin.register(TestApp)
class TestAppAdmin(admin.ModelAdmin):
    pass
