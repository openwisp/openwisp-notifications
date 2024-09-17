from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import TemplateView

User = get_user_model()


class NotificationPreferencePage(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'openwisp_notifications/preferences.html'
    login_url = reverse_lazy('admin:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('pk')
        context['title'] = _('Notification Preferences')

        if user_id:
            try:
                user = User.objects.get(pk=user_id)
                # Only admin should access other users preferences
                context['username'] = user.username
                context['title'] += f' ({user.username})'
            except User.DoesNotExist:
                raise Http404('User does not exist')
        else:
            user = self.request.user

        context['user_id'] = user.id
        return context

    def test_func(self):
        """
        This method ensures that only admins can access the view when a custom user ID is provided.
        """
        if 'pk' in self.kwargs:
            return (
                self.request.user.is_superuser
                or self.request.user.id == self.kwargs.get('pk')
            )
        return True


notification_preference_page = NotificationPreferencePage.as_view()
