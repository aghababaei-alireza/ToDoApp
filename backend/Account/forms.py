from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailAuthenticationForm(forms.Form):
    """
    Form for authentication using Email.
    """

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"autofocus": True}))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"})
    )

    error_messages = {
        "invalid_login": _(
            "Please enter a correct email and password. Note that both "
            "fields may be case-sensitive."
        ),
        "inactive": _("This account is inactive."),
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        """
        Check that the email and password are valid.
        """
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if email and password:
            self.user_cache = authenticate(
                self.request, email=email, password=password)
            if self.user_cache is None:
                self.get_invalid_login_error()
            elif not self.user_cache.is_active:
                raise forms.ValidationError(
                    self.error_messages["inactive"],
                    code="inactive"
                )
            return self.cleaned_data

        self.get_invalid_login_error()

    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in.
        """
        if not user.is_active:
            raise ValidationError(
                self.error_messages["inactive"],
                code="inactive",
            )

    def get_invalid_login_error(self):
        return ValidationError(
            self.error_messages["invalid_login"],
            code="invalid_login",
        )

    def get_user(self):
        return self.user_cache


class CustomSignupForm(forms.Form):
    """Custom form for user signup using email."""

    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={"autofocus": True}),
    )
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label=_("Confirm Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Email already exists."))

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Passwords do not match."))

        return cleaned_data

    def save(self, commit=True):
        """
        Save the user instance.
        """
        email = self.cleaned_data["email"]
        password = self.cleaned_data["password1"]

        user = User.objects.create_user(email=email, password=password)

        if commit:
            user.save()

        return user
