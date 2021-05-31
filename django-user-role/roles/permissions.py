from rest_framework.permissions import BasePermission


class IsAllowedToCustomer(BasePermission):
    """
    This class is used to create `Customer` authorization.
    """

    def has_permission(self, request, view):
        return request.user.roles.first().name == "customer"


class IsAllowedToAdmin(BasePermission):
    """
    This class is used to create `Admin` authorization.
    """

    def has_permission(self, request, view):
        return request.user.roles.first().name == "admin"
