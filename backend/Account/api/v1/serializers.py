from django.urls import reverse, resolve
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from drf_recaptcha.fields import ReCaptchaV2Field


User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password1 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'password1']

    def validate(self, attrs):
        if attrs['password'] != attrs['password1']:
            raise serializers.ValidationError(
                {"details": "Passwords do not match."})

        try:
            validate_password(attrs['password'])
        except serializers.ValidationError as e:
            raise serializers.ValidationError({"details": list(e.messages)})

        return super().validate(attrs)

    def create(self, validated_data):
        validated_data.pop('password1', None)
        return User.objects.create_user(**validated_data)


class CustomAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)
            if not user:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(
                    {"details": msg}, code='authorization')

            if not user.is_verified:
                msg = 'User is not verified.'
                raise serializers.ValidationError(
                    {"details": msg}, code='authorization')
        else:
            msg = 'Must include "username" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        data = super().validate(attrs)

        data["email"] = self.user.email
        data["user_id"] = self.user.id

        return data


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing user password.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError(
                {"details": "Old password is wrong."})

        if attrs['new_password'] != attrs['new_password1']:
            raise serializers.ValidationError(
                {"details": "Passwords do not match."})

        try:
            validate_password(attrs['new_password'])
        except serializers.ValidationError as e:
            raise serializers.ValidationError({"details": list(e.messages)})

        return super().validate(attrs)


class VerificationResendSerializer(serializers.Serializer):
    """
    Serializer for Resending the verification email.
    """
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"details": "User with this email does not exist."})

        if user.is_verified:
            raise serializers.ValidationError(
                {"details": "User is already verified."})

        attrs['user'] = user
        return super().validate(attrs)


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for resetting password.
    """
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"details": "User with this email does not exist."})

        attrs['user'] = user
        return super().validate(attrs)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming password reset.
    """
    new_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)
    captcha = ReCaptchaV2Field(
        help_text=f"Visit the '{resolve(reverse('Account:captcha'))}' endpoint to get the captcha token.")

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password1']:
            raise serializers.ValidationError(
                {"details": "Passwords do not match."})

        try:
            validate_password(attrs['new_password'])
        except serializers.ValidationError as e:
            raise serializers.ValidationError({"details": list(e.messages)})

        return super().validate(attrs)
