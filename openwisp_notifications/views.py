from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import redirect
from .models import UserProfile
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_str, force_bytes
from django.contrib.auth import login, get_user_model
from django.urls import reverse


@login_required
def resend_verification_email(request):
    user = request.user
    try:
        user_profile = user.userprofile  # Access the related UserProfile model
        if not user_profile.needs_verification:
            # Logic to resend the verification email
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            verification_url = request.build_absolute_uri(
                reverse('openwisp_notifications:verify_email', args=[uid, token])
            )
            send_mail(
                'Email Verification',
                f'Please click the following link to verify your email: {verification_url}',
                'admin@gmail.com',
                [user.email],
            )
            messages.success(request, "Verification email has been sent.")
    except ObjectDoesNotExist:
        # Handle the case where the UserProfile does not exist
        UserProfile.objects.create(user=user, needs_verification=True)
        messages.error(request, "UserProfile was missing and has been created. Please try again.")
    return redirect('admin:index')


def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user_profile = user.userprofile
        user_profile.needs_verification = False
        user_profile.save()
        login(request, user)
        messages.success(request, "Email verified successfully!")
        return redirect('admin:index')
    messages.error(request, "Invalid verification link.")
    return redirect('admin:index')