from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import CustomLoginView, CustomSignupView

app_name = 'Account'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page="Account:login"), name='logout'),
    path('signup/', CustomSignupView.as_view(), name='signup')
]
