from rest_framework import permissions


class IsStaffOrOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_superuser or getattr(request.user, "is_moderator", False):
            return True
        return obj.user.id == request.user.id


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user.id == request.user.id


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user.id == request.user.id


class IsStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser or getattr(request.user, "is_moderator", False)


class IsStaffOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_superuser or getattr(request.user, "is_moderator", False)
