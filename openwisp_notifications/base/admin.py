from django.contrib import admin
from django.utils.html import format_html, strip_tags
from django.utils.translation import ugettext_lazy as _
from openwisp_notifications.utils import _get_object_link


class AbstractNotificationAdmin(admin.ModelAdmin):
    raw_id_fields = ('recipient',)
    readonly_fields = [
        'action_object_object_link',
        'actor_object_link',
        'target_object_link',
        'related_object',
        'display_list_message',
        'message',
    ]
    list_display = ('display_list_message', 'read', 'level', 'timesince')
    list_filter = (
        'level',
        'unread',
    )
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'timestamp',
                    'type',
                    'level',
                    'message',
                    'related_object',
                    'emailed',
                )
            },
        ),
        (
            _('Advanced options'),
            {
                'classes': ('collapse',),
                'fields': (
                    'actor_content_type',
                    'actor_object_link',
                    'action_object_content_type',
                    'action_object_object_link',
                    'target_content_type',
                    'target_object_link',
                    'data',
                ),
            },
        ),
    )

    class Media:
        extend = True
        js = [
            'openwisp_notifications/js/notifications.js',
        ]

    def read(self, instance):
        return not instance.unread

    read.boolean = True
    read.short_description = _('read')

    actions = ['mark_as_read']

    def mark_as_read(self, request, queryset):
        result = queryset.filter(unread=True).update(unread=False)
        if result == 1:
            bit = '1 notification was'
        else:
            bit = '{0} notifications were'.format(result)
        message = '{0} marked as read.'.format(bit)
        self.message_user(request, _(message))

    mark_as_read.short_description = _('Mark selected notifications as read')

    def actor_object_link(self, obj):
        return _get_object_link(obj, field='actor')

    actor_object_link.short_description = _('Actor Object')

    def action_object_object_link(self, obj):
        return _get_object_link(obj, field='action_object')

    action_object_object_link.short_description = _('Action Object')

    def target_object_link(self, obj):
        return _get_object_link(obj, field='target')

    target_object_link.short_description = _('Target Object')

    def related_object(self, obj):
        target_object_url = _get_object_link(obj, field='target', html=False)
        if target_object_url.startswith('/admin/'):
            return format_html(
                '<a href="{url}" id="related-object-url">{content_type}: {name}</a>',
                url=target_object_url,
                content_type=obj.target_content_type.model,
                name=obj.target,
            )
        return target_object_url

    related_object.short_description = _('Related Object')

    def display_list_message(self, obj):
        return strip_tags(obj.message)

    display_list_message.short_description = _('Message')

    def get_queryset(self, request):
        return self.model.objects.filter(recipient=request.user)

    def get_readonly_fields(self, request, obj=None):
        fields = self.fields or [f.name for f in self.model._meta.fields]
        return fields + self.__class__.readonly_fields

    def has_add_permission(self, request):
        return False

    def render_change_form(
        self, request, context, add=False, change=True, form_url='', obj=None
    ):
        if obj and obj.unread:
            obj.unread = False
            obj.save()
        # disable save buttons
        context.update(
            {
                'add': False,
                'has_add_permission': False,
                'show_delete_link': True,
                'show_save_as_new': False,
                'show_save_and_add_another': False,
                'show_save_and_continue': False,
                'show_save': False,
            }
        )
        return super().render_change_form(
            request, context, add=add, change=change, form_url=form_url, obj=obj
        )
