from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from .serializers import UserSerializer
from django.utils.encoding import force_str  

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)

            if serializer.is_valid():
                # Create an inactive user (awaiting email verification)
                user = serializer.save(is_active=False)

                # Generate verification token and UID
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))

                # Get current site (domain) to generate the verification URL
                current_site = get_current_site(request)

                # Prepare the email content
                mail_subject = 'Activate Your Account'
                message = f"""
                Hi {user.username},

                Thank you for registering. To activate your account, please click the link below:

                {current_site.domain}/auth/verify-email/{uid}/{token}/

                If the above link doesn't work, please copy and paste it into your browser.

                This link will expire in 24 hours.

                Thank you,
                The Loan Management Team
                """

                # Send the verification email
                email = EmailMessage(
                    mail_subject,
                    message,
                    to=[user.email],
                    from_email=settings.EMAIL_HOST_USER
                )
                email.send()

                return Response({
                    "status": "success",
                    "message": "Please check your email to complete registration"
                }, status=status.HTTP_201_CREATED)

            # Return validation errors if serializer is not valid
            return Response({
                "status": "error",
                "message": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Log the exception for debugging purposes (can replace print with proper logging in production)
            print(f"Error during registration: {str(e)}")

            return Response({
                "status": "error",
                "message": "An unexpected error occurred while processing your registration."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, uidb64, token):
        try:
            # Decode the UID from the URL
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            
            # Check if the token is valid
            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()

                return Response({
                    "status": "success",
                    "message": "Email verified successfully. You can now login."
                })
            else:
                return Response({
                    "status": "error",
                    "message": "Activation link is invalid or expired."
                }, status=status.HTTP_400_BAD_REQUEST)
        
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            # Log the exception for debugging purposes (you can replace print with proper logging in production)
            print(f"Error during email verification: {str(e)}")
            
            return Response({
                "status": "error",
                "message": "The verification link is invalid or expired."
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Catch any unexpected exceptions
            print(f"Unexpected error during email verification: {str(e)}")
            return Response({
                "status": "error",
                "message": "An unexpected error occurred while verifying the email."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





from django.contrib.auth import authenticate
from .jwt_utils import CustomTokenObtainPairSerializer

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            # Get the username and password from the request data
            username = request.data.get('username')
            password = request.data.get('password')
            
            # Check if username or password is missing
            if not username or not password:
                return Response({
                    "status": "error",
                    "message": "Username and password are required."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Authenticate the user
            user = authenticate(username=username, password=password)

            if not user:
                return Response({
                    "status": "error",
                    "message": "Invalid username or password"
                }, status=status.HTTP_401_UNAUTHORIZED)

            if not user.is_active:
                return Response({
                    "status": "error",
                    "message": "Account is not activated. Please check your email."
                }, status=status.HTTP_401_UNAUTHORIZED)

            # Generate the JWT tokens using custom token serializer
            refresh = CustomTokenObtainPairSerializer.get_token(user)
            
            return Response({
                "status": "success",
                "data": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user_id": user.pk,
                    "username": user.username,
                    "is_admin": user.is_staff
                }
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Catch any unexpected errors and return an internal server error response
            print(f"Unexpected error during login: {str(e)}")
            return Response({
                "status": "error",
                "message": "An unexpected error occurred during the login process."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            # Client should discard the JWT token, as it's stateless and not stored on the server side also if needed implement token blacklisting.
            return Response({
                "status": "success",
                "message": "Successfully logged out. Please discard your token."
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Catch any unexpected errors and return an internal server error response
            print(f"Unexpected error during logout: {str(e)}")
            return Response({
                "status": "error",
                "message": "An unexpected error occurred during the logout process."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class AdminRegisterView(APIView):
    # permission_classes = [IsAdmin]  # Only admins can register new admins
    permission_classes = [permissions.AllowAny]  # Can be adjusted to IsAdmin when needed

    def post(self, request):
        try:

            # Check if the requesting user is an admin
            # if not request.user.is_staff:
            #     return Response({
            #         "status": "error",
            #         "message": "Only admins can register new admins"
            #     }, status=status.HTTP_403_FORBIDDEN)

            # Deserialize the input data
            serializer = UserSerializer(data=request.data)
            
            if serializer.is_valid():
                # Create a new admin user
                user = serializer.save(is_staff=True, is_active=True)

                # Generate refresh and access tokens for the new admin user
                # refresh = RefreshToken.for_user(user)
                refresh = CustomTokenObtainPairSerializer.get_token(user)

                return Response({
                    "status": "success",
                    "data": {
                        "user_id": user.pk,
                        "username": user.username,
                        "is_admin": True,
                        "refresh": str(refresh),
                        "access": str(refresh.access_token)
                    }
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                "status": "error",
                "message": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            # Catch any unexpected exceptions during the registration process
            print(f"Unexpected error during admin registration: {str(e)}")
            return Response({
                "status": "error",
                "message": "An unexpected error occurred during the registration process."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


