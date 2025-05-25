from django.urls import path, include
from django.contrib.auth.views import LogoutView
from .views import CustomLoginView, CustomSignupView, CustomeChangePasswordView, CustomPasswordResetView, CustomPasswordResetDoneView, CustomPasswordResetConfirmView, CustomPasswordResetCompleteView, VerificationResendView, VerificationConfirmView, VerificationRequiredView

app_name = 'Account'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page="Account:login"), name='logout'),
    path('signup/', CustomSignupView.as_view(), name='signup'),
    path('change-password/', CustomeChangePasswordView.as_view(),
         name='change-password'),
    path('reset-password/', CustomPasswordResetView.as_view(),
         name='reset-password'),
    path('reset-password/done/', CustomPasswordResetDoneView.as_view(),
         name='reset-password-done'),
    path('reset-password/confirm/<str:token>/', CustomPasswordResetConfirmView.as_view(),
         name='reset-password-confirm'),
    path('reset-password/complete/', CustomPasswordResetCompleteView.as_view(),
         name='reset-password-complete'),
    path('verify/resend/', VerificationResendView.as_view(),
         name="verification-resend"),
    path('verify/confirm/<str:token>/', VerificationConfirmView.as_view(),
         name="verification-confirm"),
    path('verified_user_required/', VerificationRequiredView.as_view(),
         name="verification-required"),
    path('api/v1/', include('Account.api.v1.urls')),
]
