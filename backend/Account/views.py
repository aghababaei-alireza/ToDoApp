from django.shortcuts import render
from django.contrib.auth.views import LoginView, PasswordResetView
from django.views.generic import FormView
from django.urls import reverse_lazy
from .forms import EmailAuthenticationForm, CustomSignupForm
from django.contrib.auth import login


class CustomLoginView(LoginView):
    """
    Custom login view that uses the default Django authentication system.
    """
    template_name = 'Account/login.html'
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('ToDo:tasks')


class CustomSignupView(FormView):
    """
    Custom signup view that uses the default Django authentication system.
    """
    template_name = 'Account/signup.html'
    form_class = CustomSignupForm
    success_url = reverse_lazy('ToDo:tasks')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)
