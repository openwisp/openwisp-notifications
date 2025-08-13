# Used for testing of openwisp-notifications
from django.contrib import admin

import openwisp_notifications.admin  # noqa: F401

from .models import TestApp


@admin.register(TestApp)
class TestAppAdmin(admin.ModelAdmin):
    pass
