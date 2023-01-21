from rest_framework import permissions


class IsAgent(permissions.BasePermission):
    """
    Global permission check for authorized agent
    """
    message = "Only agents can perform this action"

    def has_permission(self,request,view):
        user = request.user

        if not user:
            return False

        return 'agent' == user.role.lower()
            

class IsCustomer(permissions.BasePermission):
    """
    Global permission check for authorized agent
    """

    message = "Only customers can perform this action"

    def has_permission(self, request, view):
        user = request.user

        if not user:
            return False

        return 'customer' == user.role.lower()
