from rest_framework.permissions import BasePermission


class IsAuthenticatedToUpdateNotificationSetting(BasePermission):
    """
    Permission class to check if the user is authenticated to update notification settings.
    Allows superusers to change the notification preferences of other users.
    Regular users can only update their own settings.
    """

    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.id == view.kwargs.get(
            'user_id'
        )
