import swapper
from rest_framework.permissions import BasePermission

User = swapper.load_model("openwisp_users", "User")
Organization = swapper.load_model("openwisp_users", "Organization")


class PreferencesPermission(BasePermission):
    """
    Custom permission for accessing notification preferences via the API.

    Access rules:
    1. Superusers can always access any user's preferences.
    2. Users can access their own preferences.
    3. Staff users can access another user's preferences if all of the following are true:
       - They have the 'change_notificationsetting' permission.
       - They manage at least one organization that the target user belongs to.
       - If an organization_id is provided in the URL, it must be among the shared organizations.

    Returns:
        bool: True if access is allowed, False otherwise.
    """

    def has_permission(self, request, view):
        user = request.user
        target_user_id = view.kwargs.get("user_id")
        target_user = User.objects.get(id=target_user_id) if target_user_id else None
        target_org_id = view.kwargs.get("organization_id")
        target_org = (
            Organization.objects.get(id=target_org_id) if target_org_id else None
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
            shared_orgs = admin_orgs.intersection(target_orgs)

            # If an organization_id is provided, validate it’s one of the shared ones
            if target_org and target_org not in shared_orgs:
                return False

            # Allow if there’s at least one shared organization
            if shared_orgs:
                return True

        # Otherwise, deny access
        return False
