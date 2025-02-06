from django.dispatch import Signal
from django.contrib.auth.signals import user_logged_in
from django.contrib import messages
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django.utils.safestring import mark_safe
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from .models import UserProfile


@receiver(post_save, sender=get_user_model())
def create_or_save_user_profile(sender, instance, created, **kwargs):
    # If the user is newly created, create a UserProfile
    if created:
        UserProfile.objects.create(user=instance)
    # If the user already exists, ensure the profile is saved
    else:
        if hasattr(instance, 'userprofile'):
            instance.userprofile.save()
        else:
            UserProfile.objects.create(user=instance)


@receiver(user_logged_in)
def check_user_email_verified(sender, request, user, **kwargs):
    # Check if the user is a staff member
    try:
        user_profile = user.userprofile
        if user.email and not user_profile.needs_verification:
            verification_url = request.build_absolute_uri(reverse('openwisp_notifications:resend_verification_email'))
            message = _(
                "Email notifications are enabled for your account, but since your email address "
                "has not been verified, email sending is currently disabled. "
                "Please verify your email address to enable email notifications. "
                f"<a href='{verification_url}'>Verify now</a>"
            )
            messages.warning(request, mark_safe(message))
    except ObjectDoesNotExist:
        UserProfile.objects.create(user=user, needs_verification=True)
        pass


notify = Signal()
notify.__doc__ = """
Creates notification(s).

Sends arguments: 'recipient', 'actor', 'verb', 'action_object',
    'target', 'description', 'timestamp', 'level', 'type', etc.
"""
