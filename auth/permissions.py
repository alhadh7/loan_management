from rest_framework import permissions


from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Custom permission to only allow admin users using JWT payload.
    """
    def has_permission(self, request, view):
        # Check if JWT token is present (middleware already attaches request.auth)
        if not request.auth:
            return False
        
        # Check if user is Admin directly from JWT payload
        return request.auth.get("is_admin", False)


class IsUser(permissions.BasePermission):
    """
    Custom permission to only allow regular users using JWT payload.
    """
    def has_permission(self, request, view):
        # Check if JWT token is present
        if not request.auth:
            return False
        
        # Check if user is NOT Admin from JWT payload
        return not request.auth.get("is_admin", False)



# class IsOwnerOrAdmin(permissions.BasePermission):
#     """
#     Custom permission to allow loan owners or admins to access the loan details.
#     """
#     def has_object_permission(self, request, view, obj):
#         # Check if the user is the owner of the loan or an admin
#         return obj.user == request.user or request.user.is_staff
    
    
# from rest_framework import permissions
# from rest_framework_simplejwt.authentication import JWTAuthentication

# class IsAdmin(permissions.BasePermission):
#     """
#     Custom permission to only allow admin users.
#     """
#     def has_permission(self, request, view):
#         # Check if user is authenticated first
#         if not request.user.is_authenticated:
#             return False
            
#         # Check if the user is an admin based on the JWT token
#         return request.user.is_staff


# class IsUser(permissions.BasePermission):
#     """
#     Custom permission to only allow non-admin users.
#     """
#     def has_permission(self, request, view):
#         # Check if user is authenticated first
#         if not request.user.is_authenticated:
#             return False
            
#         # Check if the user is a regular user (not admin) based on the JWT token
#         return not request.user.is_staff