from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.views.generic import TemplateView

User = get_user_model()


class NotificationSettingPage(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'openwisp_notifications/settings.html'
    login_url = '/admin/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('pk')

        if user_id:
            try:
                user = User.objects.get(pk=user_id)
                # Only admin should access other users settings
                if not self.request.user.is_staff:
                    raise Http404("You do not have permission to access this page.")
            except User.DoesNotExist:
                raise Http404("User does not exist")
        else:
            user = self.request.user

        context['user'] = user
        return context

    def test_func(self):
        """
        This method ensures that only admins can access the view when a custom user ID is provided.
        """
        if 'pk' in self.kwargs:
            return self.request.user.is_staff
        return True


notifiation_setting_page = NotificationSettingPage.as_view()
