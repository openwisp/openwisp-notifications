from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, reverse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from allauth.account.utils import send_email_confirmation
from allauth.account.models import EmailAddress
from django.utils.http import is_safe_url
import logging

logger = logging.getLogger(__name__)


@login_required
def resend_verification_email(request):
    user = request.user
    email_address = None

    primary_email = EmailAddress.objects.filter(user=user, primary=True).first()
    if primary_email:
        email_address = primary_email
    else:
        last_email = EmailAddress.objects.filter(user=user).order_by('-id').first()
        if last_email:
            email_address = last_email
        elif user.email:
            email_address = EmailAddress.objects.create(
                user=user,
                email=user.email,
                primary=True,
                verified=False
            )
        else:
            messages.info(request, _("No email address found for your account."))

    if email_address:
        if email_address.verified:
            messages.info(request, _("Your email is already verified."))
        else:
            send_email_confirmation(request, user, email=email_address.email)
            messages.success(request, _("Verification email has been sent."))
    redirect_to = request.GET.get('next', reverse('admin:index'))
    if not is_safe_url(redirect_to, allowed_hosts={request.get_host()}):
        logger.warning(f"Unsafe redirect attempted to: {redirect_to} for user {user.username}")
        redirect_to = reverse('admin:index')
    return redirect(redirect_to)
