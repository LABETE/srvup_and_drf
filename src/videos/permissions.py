from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied


class IsMember(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated() or view.get_object().free_preview:
            try:
                is_member = request.user.is_member
            except:
                is_member = None
            if is_member or view.get_object().free_preview:
                return True
            raise PermissionDenied("You must be a member for watch this video.")
        raise PermissionDenied("You must be logged in.")

