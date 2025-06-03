from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.urls import reverse


class VerifiedUserRequiredMixin(AccessMixin):
    """Verify that the logged-in user is email-verified."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not getattr(request.user, "is_verified", False):
            return redirect(reverse("Account:verification-required"))

        return super().dispatch(request, *args, **kwargs)
