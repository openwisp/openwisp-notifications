from django.dispatch import Signal
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib import messages
from django.urls import reverse
from django.utils.html import format_html
from allauth.account.models import EmailAddress


@receiver(user_logged_in)
def check_email_verification(sender, user, request, **kwargs):
    if user.is_staff and request.path.startswith('/admin/'):
        has_email = user.email or EmailAddress.objects.filter(user=user).exists()
        if has_email:
            has_verified_email = EmailAddress.objects.filter(user=user, verified=True).exists()
            if not has_verified_email:
                resend_url = reverse('notifications:resend_verification_email')
                message = format_html(
                    'Email notifications are enabled for your account, but since your email address has not been verified, '
                    'email sending is currently disabled. Please <a href="{}">resend the verification email</a> to verify your email address.',
                    resend_url
                )
                messages.warning(request, message)


notify = Signal()
notify.__doc__ = """
Creates notification(s).

Sends arguments: 'recipient', 'actor', 'verb', 'action_object',
    'target', 'description', 'timestamp', 'level', 'type', etc.
"""
