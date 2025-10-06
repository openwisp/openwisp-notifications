import base64
import json
import logging

from allauth.account.models import EmailAddress
from allauth.account.utils import send_email_confirmation
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render, reverse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme as is_safe_url
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from openwisp_notifications.swapper import load_model

from .tokens import email_token_generator

User = get_user_model()
NotificationSetting = load_model("NotificationSetting")

logger = logging.getLogger(__name__)


@login_required
def resend_verification_email(request):
    user = request.user
    # check if user has a primary email address
    email_address = EmailAddress.objects.filter(user=user, primary=True).first()
    if not email_address:
        # if the user doesn't have a primary email address
        # get the last email address added
        email_address = EmailAddress.objects.filter(user=user).order_by("-id").first()
        # if the user doesn't have any EmailAddress object saved
        # get the email address from the User model
        if not email_address and user.email:
            email_address = EmailAddress.objects.create(
                user=user, email=user.email, primary=True, verified=False
            )
        elif not email_address and not user.email:
            messages.error(request, _("No email address found for your account."))
    # if email is already verified, just display a UX warning
    if email_address and email_address.verified:
        messages.warning(request, _("Your email is already verified."))
    # if email is not verified, resend verification email
    elif email_address and not email_address.verified:
        send_email_confirmation(request, user, email=email_address.email)
    # block malicious redirect attempts
    redirect_to = request.GET.get("next", reverse("admin:index"))
    if not is_safe_url(redirect_to, allowed_hosts={request.get_host()}):
        logger.warning(
            f"Unsafe redirect attempted to: {redirect_to} for user {user.username}."
        )
        redirect_to = reverse("admin:index")
    # redirect to where the user was headed after logging in
    return redirect(redirect_to)


class NotificationPreferenceView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "openwisp_notifications/preferences.html"
    login_url = reverse_lazy("admin:login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get("pk")
        context["title"] = _("Notification Preferences")

        if user_id:
            try:
                user = User.objects.get(pk=user_id)
                # Only admin should access other users preferences
                context["username"] = user.username
                context["title"] += f" ({user.username})"
            except User.DoesNotExist:
                raise Http404("User does not exist")
        else:
            user = self.request.user

        context["user_id"] = user.id
        return context

    def test_func(self):
        """
        Determines whether the current user can view or modify another user's
        notification preferences.

        Access rules:
        1. Superusers can always access any user's preferences.
        2. Users can access their own preferences.
        3. Staff users can access another user's preferences if all of the following are true:
           - They have the 'change_notificationsetting' permission.
           - They manage at least one organization that the target user belongs to.

        Returns:
            bool: True if access is allowed, False otherwise.
        """
        user = self.request.user
        target_user_id = self.kwargs.get("pk")
        target_user = (
            User.objects.filter(id=target_user_id).first() if target_user_id else None
        )

        # Superusers always have access
        if user.is_superuser:
            return True

        # Users can access their own preferences
        if target_user_id and user.id == target_user_id:
            return True

        # Staff users with proper permission can access users in their managed orgs
        if user.is_staff and user.has_perm(
            "openwisp_notifications.change_notificationsetting"
        ):
            admin_orgs = set(user.organizations_managed)
            target_orgs = set(target_user.organizations_dict.keys())

            # Allow if staff manages at least one org the target user belongs to
            if admin_orgs.intersection(target_orgs):
                return True

        # Otherwise, deny access
        return False


@method_decorator(csrf_exempt, name="dispatch")
class UnsubscribeView(TemplateView):
    template_name = "openwisp_notifications/unsubscribe.html"

    def dispatch(self, request, *args, **kwargs):
        self.encoded_token = request.GET.get("token")
        if not self.encoded_token:
            if request.method == "POST":
                return JsonResponse(
                    {"success": False, "message": "No token provided"}, status=400
                )
            return render(request, self.template_name, {"valid": False})

        self.user, self.valid = self._validate_token(self.encoded_token)
        if not self.valid:
            if request.method == "POST":
                return JsonResponse(
                    {"success": False, "message": "Invalid or expired token"},
                    status=400,
                )
            return render(request, self.template_name, {"valid": False})

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_subscribed = self.get_user_preference(self.user) if self.valid else False
        context.update(
            {
                "valid": self.valid,
                "is_subscribed": is_subscribed,
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        try:
            if request.content_type == "application/json":
                data = json.loads(request.body)
                subscribe = data.get("subscribe", False) is True
            else:
                # Unsubscribe by default
                subscribe = False
        except json.JSONDecodeError:
            return JsonResponse(
                {"success": False, "message": "Invalid JSON data"}, status=400
            )

        self.update_user_preferences(self.user, subscribe)
        status_message = "subscribed" if subscribe else "unsubscribed"
        return JsonResponse(
            {"success": True, "message": f"Successfully {status_message}"}
        )

    def _validate_token(self, encoded_token):
        try:
            decoded_data = urlsafe_base64_decode(encoded_token).decode("utf-8")
            data = json.loads(decoded_data)
            user_id = data.get("user_id")
            token = data.get("token")

            user = User.objects.get(id=user_id)
            if email_token_generator.check_token(user, token):
                return user, True
        except (
            User.DoesNotExist,
            ValueError,
            json.JSONDecodeError,
            base64.binascii.Error,
        ):
            pass

        return None, False

    def get_user_preference(self, user):
        """
        Check if any of the user's notification settings have email notifications enabled.
        """
        return NotificationSetting.objects.filter(user=user, email=True).exists()

    def update_user_preferences(self, user, subscribe):
        """
        Update all of the user's notification settings to set email preference.
        """
        NotificationSetting.objects.filter(user=user).update(email=subscribe)


notification_preference_view = NotificationPreferenceView.as_view()
unsubscribe_view = UnsubscribeView.as_view()
