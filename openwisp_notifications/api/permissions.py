from rest_framework.permissions import BasePermission


class IsAuthenticatedToUpdateNotificationSetting(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        user_id = view.kwargs.get('user_id')

        # Allow superusers
        if user.is_superuser:
            return True

        # Allow users to update their own settings
        if user.id == user_id:
            return True

        return False
