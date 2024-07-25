from openwisp_notifications.swapper import load_model
from openwisp_users.api.filters import OrganizationMembershipFilter

NotificationSetting = load_model('NotificationSetting')


class NotificationSettingFilter(OrganizationMembershipFilter):
    class Meta(OrganizationMembershipFilter.Meta):
        model = NotificationSetting
        fields = OrganizationMembershipFilter.Meta.fields + ['type']

    @property
    def qs(self):
        parent_qs = super().qs
        return parent_qs.exclude(organization__isnull=True, type__isnull=True)
