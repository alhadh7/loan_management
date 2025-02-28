from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from auth.jwt_utils import CustomTokenObtainPairView
from .views import (
    RegisterView, VerifyEmailView, LoginView, LogoutView, AdminRegisterView
)
urlpatterns = [ 

path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/<str:uidb64>/<str:token>/', VerifyEmailView.as_view(), name='verify_email'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('admin/register/', AdminRegisterView.as_view(), name='admin_register'),

    ]