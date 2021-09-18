from openwisp_notifications.base.forms import NotificationSettingForm


class NotificationSettingAdminMixin:
    fields = ['type', 'organization', 'web', 'email', 'deleted']
    readonly_fields = [
        'type',
        'organization',
    ]
    form = NotificationSettingForm

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return list()
        else:
            return self.readonly_fields

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request)
        if not request.user.is_superuser and 'deleted' in fields:
            fields.remove('deleted')
        return fields

    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        # A notification is considered deleted when the delete
        # boolean field is set. A user can never delete
        # NotificationSettting from the database.
        return False

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .filter(deleted=False)
            .prefetch_related('organization')
        )

    class Media:
        extends = True
        js = [
            'admin/js/jquery.init.js',
            'openwisp-notifications/js/notification-settings.js',
        ]
