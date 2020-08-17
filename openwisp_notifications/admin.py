from django.contrib import admin

from openwisp_notifications.swapper import load_model
from openwisp_users.admin import UserAdmin
from openwisp_utils.admin import AlwaysHasChangedMixin

Notification = load_model('Notification')
NotificationUser = load_model('NotificationUser')


class NotificationUserInline(AlwaysHasChangedMixin, admin.StackedInline):
    model = NotificationUser
    fields = ['receive', 'email']


UserAdmin.inlines.insert(len(UserAdmin.inlines) - 1, NotificationUserInline)
