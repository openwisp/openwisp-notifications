class NotificationSettingAdminMixin:
    fields = ['type', 'organization', 'web', 'email']
    readonly_fields = [
        'type',
        'organization',
    ]
    empty_value_display = 'All'

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return list()
        else:
            return self.readonly_fields

    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'organization':
            kwargs['empty_label'] = 'All'
        return super().formfield_for_dbfield(db_field, request, **kwargs)
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('organization')
