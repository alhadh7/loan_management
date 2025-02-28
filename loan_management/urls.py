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

# urls.py (main project)
from django.contrib import admin
from django.urls import path, include

handler400 = 'loans.views.custom_400'
handler403 = 'loans.views.custom_403'
handler404 = 'loans.views.custom_404'
handler405 = 'loans.views.custom_405'
handler500 = 'loans.views.custom_500'

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('api/', include('loans.urls')),
    path('auth/', include('auth.urls')),

]