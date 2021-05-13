from rest_framework import permissions


class IsCurrentOrReadOnly(permissions.BasePermission):
    message = "You don't have permission for this user"

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user
