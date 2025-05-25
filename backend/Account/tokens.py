from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import AbstractUser
import jwt
from django.conf import settings


class TokenGenerator:
    @classmethod
    def make_token(cls, user: AbstractUser) -> str:
        """
        Generates a token for the given user.
        """
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    @classmethod
    def check_token(cls, token: str) -> int:
        """
        Checks if the given token is valid.
        """
        token = jwt.decode(token, settings.SECRET_KEY, "HS256")
        return token["user_id"]
