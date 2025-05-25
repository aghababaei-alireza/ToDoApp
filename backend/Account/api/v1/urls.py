from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView
)
from .views import RegistrationView, CustomAuthToken, LogoutView, CustomTokenObtainPairView, ChangePasswordAPIView, VerificationResendAPIView, PasswordResetAPIView

app_name = "API"

urlpatterns = [
    # Token Authentication
    path("registeration/", RegistrationView.as_view(), name="token-registeration"),
    path('login/', CustomAuthToken.as_view(), name='token-login'),
    path('logout/', LogoutView.as_view(), name='token-logout'),

    # JWT Authentication
    path('jwt/create/', CustomTokenObtainPairView.as_view(), name="jwt-create"),
    path('jwt/refresh/', TokenRefreshView.as_view(), name="jwt-refresh"),
    path('jwt/verify/', TokenVerifyView.as_view(), name="jwt-verify"),

    # Password
    path('change-password/', ChangePasswordAPIView.as_view(), name='change-password'),
    path('reset-password/', PasswordResetAPIView.as_view(), name='change-password'),

    # Verification
    path('verify/resend/', VerificationResendAPIView.as_view(),
         name="verification-resend"),
]
