from rest_framework import permissions


class IsAgent(permissions.BasePermission):
    """
    Global permission check for authorized agent
    """

    def has_permission(self,request,view):
        user = request.user

        if not user:
            return False

        return 'agent' in user.role.lower()
            