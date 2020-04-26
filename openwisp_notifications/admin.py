from django.contrib import admin
from openwisp_notifications.base.admin import AbstractNotificationAdmin
from swapper import load_model

from openwisp_users.admin import UserAdmin
from openwisp_utils.admin import AlwaysHasChangedMixin

from .models import NotificationUser

Notification = load_model('openwisp_notifications', 'Notification')


@admin.register(Notification)
class NotificationAdmin(AbstractNotificationAdmin):
    def mark_as_read(self, request, queryset):
        super().mark_as_read(request, queryset)
        Notification.invalidate_cache(request.user)


class NotificationUserInline(AlwaysHasChangedMixin, admin.StackedInline):
    model = NotificationUser
    fields = ('receive', 'email')


UserAdmin.inlines.insert(len(UserAdmin.inlines) - 1, NotificationUserInline)
