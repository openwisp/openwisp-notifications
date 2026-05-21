from rest_framework.permissions import BasePermission

from openwisp_notifications.swapper import load_model

NotificationSetting = load_model("NotificationSetting")


class PreferencesPermission(BasePermission):
    """
    Permission class for the notification preferences.

    Permission is granted in these cases:
    1. Superusers can change the notification preferences of any user.
    2. Staff users with "change_notificationsetting" permission can change
       the notification preferences of any user.
    3. Regular users can only change their own preferences.
    """

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        perm = f"{NotificationSetting._meta.app_label}.change_{NotificationSetting._meta.model_name}"
        if request.user.has_perm(perm):
            return True
        return str(request.user.id) == str(view.kwargs.get("user_id"))
