from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetDoneView, PasswordResetCompleteView
from django.views.generic import FormView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth import login, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMessage
from django.template import loader
from django.contrib.sites.shortcuts import get_current_site
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from Account.tokens import TokenGenerator
from .forms import EmailAuthenticationForm, CustomSignupForm, CustomPasswordResetForm, CustomPasswordResetConfirmForm


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
    success_url = reverse_lazy('Account:verification-resend')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)


class CustomeChangePasswordView(PasswordChangeView):
    """
    Custom change password view that uses the default Django authentication system.
    """
    template_name = 'Account/change_password.html'
    success_url = reverse_lazy('ToDo:tasks')


class CustomPasswordResetView(PasswordResetView):
    """
    Custom password reset view that uses the default Django authentication system.
    """
    template_name = 'Account/reset_password.html'
    email_template_name = 'Account/password_reset_email.html'
    subject_template_name = 'Account/password_reset_subject.txt'
    success_url = reverse_lazy('Account:reset-password-done')
    form_class = CustomPasswordResetForm
    token_generator = TokenGenerator()

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        self.request.session['password_reset_email'] = email
        return super().form_valid(form)


class CustomPasswordResetDoneView(PasswordResetDoneView):
    """
    Custom password reset done view that uses the default Django authentication system.
    """
    template_name = 'Account/reset_password_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['email'] = self.request.session.get('password_reset_email')

        if context['email']:
            del self.request.session['password_reset_email']

        return context


class CustomPasswordResetConfirmView(FormView):
    """
    Custom password reset confirm view that uses JWT authentication system.
    """
    template_name = 'Account/reset_password_confirm.html'
    form_class = CustomPasswordResetConfirmForm
    success_url = reverse_lazy("Account:reset-password-complete")

    def get(self, request, *args, **kwargs):
        token = kwargs.get('token')
        context = self.get_context_data(**kwargs)
        try:
            user_id = TokenGenerator.check_token(token)
            context.update({"user_id": user_id})
        except ValueError as e:
            context.update({"error": str(e)})
        except ExpiredSignatureError:
            context.update({"error": "Token is expired."})
        except InvalidTokenError:
            context.update({"error": "Invalid Token."})
        return self.render_to_response(context)

    def form_valid(self, form):
        user_id = form.cleaned_data.get("user_id", None)
        password = form.cleaned_data.get("new_password1", None)

        user = get_user_model().objects.get(pk=user_id)
        user.set_password(password)
        user.save()
        return super().form_valid(form)


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'Account/reset_password_complete.html'


class VerificationResendView(LoginRequiredMixin, TemplateView):
    template_name = 'Account/verification_email_resent.html'

    def get(self, request, *args, **kwargs):
        user = request.user
        subject = 'ToDoApp: Verify Account'
        template_name = 'Account/verification_email.html'
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
        context = {
            "domain": domain,
            "site_name": site_name,
            "protocol": "http",
            "token": TokenGenerator.make_token(user)
        }
        body = loader.render_to_string(template_name, context)
        email = EmailMessage(subject, body, None, [user.email])
        email.send()
        return super().get(request, *args, **kwargs)


class VerificationConfirmView(TemplateView):
    template_name = 'Account/verification_confirmed.html'

    def get(self, request, *args, **kwargs):
        token = kwargs.get('token')
        context = self.get_context_data(**kwargs)
        try:
            user_id = TokenGenerator.check_token(token)
            user = get_user_model().objects.get(pk=user_id)
            user.is_verified = True
            print(f'{80*"*"}\nUSER = {user}\nVERIFIED = {user.is_verified}\n{80*"*"}')
            user.save()
        except ValueError as e:
            context.update({"error": str(e)})
        except ExpiredSignatureError:
            context.update({"error": "Token is expired."})
        except InvalidTokenError:
            context.update({"error": "Invalid Token."})
        return self.render_to_response(context)


class VerificationRequiredView(TemplateView):
    template_name = 'Account/email_verification_required.html'


class CaptchaVeiw(TemplateView):
    template_name = 'Account/captcha.html'
