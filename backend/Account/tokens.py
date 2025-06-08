from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import AbstractUser
import jwt
from django.conf import settings
from jose import jwe
from jose.exceptions import JWEError, JWEParseError


class TokenGenerator:
    @classmethod
    def make_token(cls, user: AbstractUser) -> str:
        """
        Generates a token for the given user.
        """
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        key = settings.SECRET_KEY[:32]
        enc = jwe.encrypt(str(access), key, algorithm="dir", encryption="A256GCM")
        return enc.decode("utf-8")

    @classmethod
    def check_token(cls, token: str) -> int:
        """
        Checks if the given token is valid.
        """
        key = settings.SECRET_KEY.encode()[:32]
        try:
            dec = jwe.decrypt(token, key)
        except (JWEError, JWEParseError):
            raise ValueError({"detail": "Invalid token."})
        token = jwt.decode(dec, settings.SECRET_KEY, "HS256")
        return token["user_id"]
