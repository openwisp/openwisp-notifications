from rest_framework.permissions import BasePermission


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
        if request.user.has_perm("openwisp_notifications.change_notificationsetting"):
            return True
        return str(request.user.id) == str(view.kwargs.get("user_id"))
