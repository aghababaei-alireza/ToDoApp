from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import get_user_model
from django.template import loader
from django.core.mail import EmailMessage
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from Account.tokens import TokenGenerator
from .serializers import (
    RegistrationSerializer,
    CustomTokenObtainPairSerializer,
    CustomAuthTokenSerializer,
    ChangePasswordSerializer,
    VerificationResendSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
)


class RegistrationView(GenericAPIView):
    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)

        # Send verification email
        subject = "ToDoApp: Verify Account"
        template_name = "Account/verification_email.html"
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
        context = {
            "domain": domain,
            "site_name": site_name,
            "protocol": "http",
            "token": TokenGenerator.make_token(user),
        }
        body = loader.render_to_string(template_name, context)
        email = EmailMessage(subject, body, None, [user.email])
        email.send()

        data = {"email": user.email, "token": token.key}

        return Response(data, status=status.HTTP_201_CREATED)


class CustomAuthToken(ObtainAuthToken):
    """
    Custom Auth Token view to return user email and token.
    """

    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        data = {"email": user.email, "token": token.key}
        return Response(data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    View to handle user logout.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            request.user.auth_token.delete()
            return Response(
                {"details": "Successfully logged out."},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Token.DoesNotExist:
            return Response(
                {"details": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class ChangePasswordAPIView(GenericAPIView):
    """
    View to handle password change.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response(
            {"details": "Password changed successfully."},
            status=status.HTTP_200_OK,
        )


class VerificationResendAPIView(GenericAPIView):
    serializer_class = VerificationResendSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        # Send verification email
        subject = "ToDoApp: Verify Account"
        template_name = "Account/verification_email.html"
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
        context = {
            "domain": domain,
            "site_name": site_name,
            "protocol": "http",
            "token": TokenGenerator.make_token(user),
            "using_api": True,
        }
        body = loader.render_to_string(template_name, context)
        email = EmailMessage(subject, body, None, [user.email])
        email.send()
        return Response(
            {"details": "Verification email sent."}, status=status.HTTP_200_OK
        )


class PasswordResetAPIView(GenericAPIView):
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        # Send password reset email
        subject = "ToDoApp: Password Reset"
        template_name = "Account/password_reset_email.html"
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
        context = {
            "domain": domain,
            "site_name": site_name,
            "protocol": "http",
            "token": TokenGenerator.make_token(user),
            "using_api": True,
        }
        body = loader.render_to_string(template_name, context)
        email = EmailMessage(subject, body, None, [user.email])
        email.send()
        return Response(
            {"details": "Password reset email sent."},
            status=status.HTTP_200_OK,
        )


class VerificationConfirmAPIView(APIView):
    """
    View to confirm user email verification.
    """

    def get(self, request, token, *args, **kwargs):
        try:
            user_id = TokenGenerator.check_token(token)
        except ValueError:
            return Response(
                {"details": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ExpiredSignatureError:
            return Response(
                {"details": "Token is expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except InvalidTokenError:
            return Response(
                {"details": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = get_user_model().objects.get(pk=user_id)
        if user is None:
            return Response(
                {"details": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user.is_verified:
            return Response(
                {"details": "Email is already verified."},
                status=status.HTTP_200_OK,
            )
        user.is_verified = True
        user.save()
        return Response(
            {"details": "Email verified successfully."},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmAPIView(GenericAPIView):
    """
    View to confirm password reset.
    """

    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, token, *args, **kwargs):
        try:
            user_id = TokenGenerator.check_token(token)
        except ValueError:
            return Response(
                {"details": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ExpiredSignatureError:
            return Response(
                {"details": "Token is expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except InvalidTokenError:
            return Response(
                {"details": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = get_user_model().objects.get(pk=user_id)
        if user is None:
            return Response(
                {"details": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response(
            {"details": "Password reset successfully."},
            status=status.HTTP_200_OK,
        )
