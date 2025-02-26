from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from allauth.account.utils import send_email_confirmation
from allauth.account.models import EmailAddress


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
            messages.info(request, "No email address found for your account.")
            return redirect('admin:index')

    if email_address:
        if email_address.verified:
            messages.info(request, "Your email is already verified.")
        else:
            send_email_confirmation(request, user, email=email_address.email)
            messages.success(request, "Verification email has been sent.")

    return redirect('admin:index')
