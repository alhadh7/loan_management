"""
URL configuration for loan_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse  # Import JsonResponse

def base_view(request):
    return JsonResponse({"message":"Welcome to the API. Please visit the /api/ or /auth/ endpoint for further usage."})

# Define error handlers
handler400 = 'loans.views.custom_400'
handler403 = 'loans.views.custom_403'
handler404 = 'loans.views.custom_404'
handler405 = 'loans.views.custom_405'
handler500 = 'loans.views.custom_500'

urlpatterns = [
    # path('admin/', admin.site.urls),

    # API and Auth URLs
    path('api/', include('loans.urls', namespace='loans')),
    path('auth/', include('auth.urls', namespace='auth')),

    # Base view
    path('', base_view, name='base'),
]

