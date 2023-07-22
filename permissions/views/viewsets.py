from rest_framework import permissions


class OwnsOrder(permissions.BasePermission):

    edit_methods = ("PUT", "PATCH", "POST", "GET")

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if request.method in permissions.SAFE_METHODS:
            return True

        if obj.contact == request.user.contact:
            return True

        if request.user.is_staff and request.method not in self.edit_methods:
            return True

        return False