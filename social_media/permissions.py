from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):

    message = "You must be the owner to perform this action."

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.email == request.user


class AnonPermissionOnly(permissions.BasePermission):

    message = "You are already authenticated."

    def has_permission(self, request, view):
        return not request.user.is_authenticated
