from rest_framework.permissions import SAFE_METHODS, BasePermission

from openwisp_notifications.swapper import load_model, swapper_load_model

NotificationSetting = load_model("NotificationSetting")
OrganizationUser = swapper_load_model("openwisp_users", "OrganizationUser")


class PreferencesPermission(BasePermission):
    """
    Permission class for the notification preferences.

    Permission is granted in these cases:
    1. Superusers can change the notification preferences of any user.
    2. Users with the required NotificationSetting permission can access
       the notification preferences of another user in a managed organization.
    3. All other authenticated users can only change their own preferences.
       This includes deprecated routes without a user_id URL parameter.
    """

    def _get_perm(self, action):
        """Return the active NotificationSetting model permission."""
        return (
            f"{NotificationSetting._meta.app_label}."
            f"{action}_{NotificationSetting._meta.model_name}"
        )

    def _has_required_perm(self, request):
        """
        Match Django model permission semantics for preferences API methods.

        Read requests accept view or change permission because users with
        change permission should be able to inspect settings before editing.
        Write requests require change permission.
        """
        if request.method in SAFE_METHODS:
            return request.user.has_perm(
                self._get_perm("view")
            ) or request.user.has_perm(self._get_perm("change"))
        return request.user.has_perm(self._get_perm("change"))

    def _can_access_target_user(self, request, view):
        """
        Check whether the requested user belongs to a managed organization.

        This is used only for other-user access. Own preferences and
        superuser access are handled separately in ``has_permission``.
        """
        user_id = view.kwargs.get("user_id")
        queryset = OrganizationUser.objects.filter(
            user_id=user_id,
            organization_id__in=request.user.organizations_managed,
        )
        organization_id = view.kwargs.get("organization_id")
        # Bulk organization updates must target an organization the requester
        # manages and the target user belongs to.
        if organization_id is not None:
            queryset = queryset.filter(organization_id=organization_id)
        return queryset.exists()

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        user_id = view.kwargs.get("user_id")
        if user_id is None:
            return True
        if str(request.user.id) == str(user_id):
            return True
        return self._has_required_perm(request) and self._can_access_target_user(
            request, view
        )
