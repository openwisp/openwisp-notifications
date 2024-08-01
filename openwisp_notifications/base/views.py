from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class NotificationSettingPage(LoginRequiredMixin, TemplateView):
    template_name = 'openwisp_notifications/settings.html'
    login_url = '/admin/login/'


notifiation_setting_page = NotificationSettingPage.as_view()
