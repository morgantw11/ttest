from rest_framework.permissions import BasePermission


ROLE_HIERARCHY = {
    'super_admin': 4,
    'admin': 3,
    'worker': 2,
    'user': 1
}

class IsWorkerOrMore(BasePermission):
    
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        user_value = ROLE_HIERARCHY.get(user.role, 0)
        min_value = ROLE_HIERARCHY.get('worker', 0)

        return user_value >= min_value
    
class IsAdminOrMore(BasePermission):
    
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        user_value = ROLE_HIERARCHY.get(user.role, 0)
        min_value = ROLE_HIERARCHY.get('admin', 0)
        
        return user_value >= min_value
    
class IsSuperAdmin(BasePermission):
    
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        user_value = ROLE_HIERARCHY.get(user.role, 0)
        min_value = ROLE_HIERARCHY.get('super_admin', 0)
        
        return user_value >= min_value
