"""
URL configuration for core_api project.

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
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from coursework.ai_views import ChatWithPDFView

# Imported the new ResendOTPView here
from coursework.auth_views import RegisterView, VerifyOTPView, ResendOTPView 

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth Endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Registration & Verification Endpoints
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/verify-otp/', VerifyOTPView.as_view(), name='verify_email'),
    
    # NEW: Resend OTP Endpoint
    path('api/resend-otp/', ResendOTPView.as_view(), name='resend_otp'),
    
    path('api/documents/<int:document_id>/chat/', ChatWithPDFView.as_view(), name='chat_with_pdf'),
    
    # Documents
    path('api/', include('coursework.urls')), 
]