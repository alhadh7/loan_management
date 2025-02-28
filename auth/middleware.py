# Add this to a new file named middleware.py

from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from django.http import JsonResponse


class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith('/auth/register/') or \
           request.path.startswith('/auth/login/') or \
           request.path.startswith('/auth/verify-email/'):
            return None

        jwt_authenticator = JWTAuthentication()

        try:
            header = jwt_authenticator.get_header(request)
            if header is None:
                return None

            raw_token = jwt_authenticator.get_raw_token(header)
            if raw_token is None:
                return None

            validated_token = jwt_authenticator.get_validated_token(raw_token)

            # Only use JWT data without DB
            request.auth = validated_token
            request.is_admin = validated_token.get("is_admin", False)

        except (InvalidToken, AuthenticationFailed):
            return None

        return None



# class JWTAuthenticationMiddleware(MiddlewareMixin):
#     """
#     Middleware to process JWT token and set user role information in request
#     """
    
#     def process_request(self, request):
#         # Skip authentication for paths that don't require it
#         if request.path.startswith('/auth/register/') or \
#            request.path.startswith('/auth/login/') or \
#            request.path.startswith('/auth/verify-email/'):
#             return None
            
#         jwt_authenticator = JWTAuthentication()
        
#         # Try to authenticate using JWT
#         try:
#             header = jwt_authenticator.get_header(request)
#             if header is None:
#                 return None
                
#             raw_token = jwt_authenticator.get_raw_token(header)
#             if raw_token is None:
#                 return None
                
#             validated_token = jwt_authenticator.get_validated_token(raw_token)
            
#             # Set user info in request
#             request.user, request.auth = jwt_authenticator.get_user(validated_token), validated_token
            
#             # Extract role information for easy access
#             request.is_admin = request.user.is_staff
            
#         except (InvalidToken, AuthenticationFailed):
#             # Don't raise an exception here, just let the view handle it
#             # with proper permission checks
#             return None
            
#         return None