import logging

from allauth.account.models import EmailAddress
from allauth.account.utils import send_email_confirmation
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, reverse
from django.utils.http import url_has_allowed_host_and_scheme as is_safe_url
from django.utils.translation import gettext_lazy as _

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
        messages.success(request, _('The verification email has been sent again.'))
    # block malicious redirect attempts
    redirect_to = request.GET.get('next', reverse('admin:index'))
    if not is_safe_url(redirect_to, allowed_hosts={request.get_host()}):
        logger.warning(
            f'Unsafe redirect attempted to: {redirect_to} for user {user.username}.'
        )
        redirect_to = reverse('admin:index')
    # redirect to where the user was headed after logging in
    return redirect(redirect_to)
