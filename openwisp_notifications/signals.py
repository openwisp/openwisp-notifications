from django.dispatch import Signal
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib import messages
from django.urls import reverse
from django.utils.html import format_html
from allauth.account.models import EmailAddress
from urllib.parse import quote
from django.utils.translation import gettext_lazy as _


@receiver(user_logged_in)
def check_email_verification(sender, user, request, **kwargs):
    if user.is_staff and request.path.startswith('/admin/'):
        has_verified_email = EmailAddress.objects.filter(user=user, verified=True).exists()
        if not has_verified_email and user.email:
            current_path = quote(request.path)
            resend_url = f"{reverse('notifications:resend_verification_email')}?next={current_path}"
            message = format_html(
                _('Email notifications are enabled for your account, but since your email address has not been verified, '
                'email sending is currently disabled. Please <a href="{}">resend the verification email</a> to verify your email address.'),
                resend_url
            )
            messages.warning(request, message)


notify = Signal()
notify.__doc__ = """
Creates notification(s).

Sends arguments: 'recipient', 'actor', 'verb', 'action_object',
    'target', 'description', 'timestamp', 'level', 'type', etc.
"""
