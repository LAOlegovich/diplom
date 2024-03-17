from rest_framework.permissions import BasePermission

class IsOwnerOrAdmin(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.id == obj.user_id or request.user.type == '3':
            return True
        else:
            return False