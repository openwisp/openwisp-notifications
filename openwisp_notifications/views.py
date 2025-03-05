import logging

from allauth.account.models import EmailAddress
from allauth.account.utils import send_email_confirmation
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.shortcuts import redirect, reverse
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme as is_safe_url
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

User = get_user_model()

logger = logging.getLogger(__name__)


@login_required
def resend_verification_email(request):
    user = request.user
    # check if user has a primary email address
    email_address = EmailAddress.objects.filter(user=user, primary=True).first()
    if not email_address:
        # if the user doesn't have a primary email address
        # get the last email address added
        email_address = EmailAddress.objects.filter(user=user).order_by('-id').first()
        # if the user doesn't have any EmailAddress object saved
        # get the email address from the User model
        if not email_address and user.email:
            email_address = EmailAddress.objects.create(
                user=user, email=user.email, primary=True, verified=False
            )
        elif not email_address and not user.email:
            messages.error(request, _('No email address found for your account.'))
    # if email is already verified, just display a UX warning
    if email_address and email_address.verified:
        messages.warning(request, _('Your email is already verified.'))
    # if email is not verified, resend verification email
    elif email_address and not email_address.verified:
        send_email_confirmation(request, user, email=email_address.email)
    # block malicious redirect attempts
    redirect_to = request.GET.get('next', reverse('admin:index'))
    if not is_safe_url(redirect_to, allowed_hosts={request.get_host()}):
        logger.warning(
            f'Unsafe redirect attempted to: {redirect_to} for user {user.username}.'
        )
        redirect_to = reverse('admin:index')
    # redirect to where the user was headed after logging in
    return redirect(redirect_to)


class NotificationPreferencePage(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'openwisp_notifications/preferences.html'
    login_url = reverse_lazy('admin:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('pk')
        context['title'] = _('Notification Preferences')

        if user_id:
            try:
                user = User.objects.only('id', 'username').get(pk=user_id)
                # Only admin should access other users preferences
                context['username'] = user.username
                context['title'] += f' ({user.username})'
            except User.DoesNotExist:
                raise Http404(_('User does not exist'))
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
