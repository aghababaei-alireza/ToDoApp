from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Write permissions are only allowed to the owner of the snippet.
        return obj.user == request.user


class IsVerified(permissions.BasePermission):
    """
    Custom permission to only allow verified users to access the view.
    """

    message = "Your email address is not verified. Please verify your email to continue."

    def has_permission(self, request, view):
        # Check if the user is verified
        return request.user.is_verified
