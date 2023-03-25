from rest_framework import permissions


class IsStaffOrOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user is not None

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.is_moderator:
            return True
        return obj.user_id == request.user
