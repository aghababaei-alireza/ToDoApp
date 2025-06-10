import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.response import Response
from Account.models import User
from rest_framework.authtoken.models import Token


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def verified_user() -> User:
    user = User.objects.create_user(email="test@example.com", password="pass@1234*", is_verified=True)
    return user


@pytest.fixture
def unverified_user() -> User:
    user = User.objects.create_user(email="test@example.com", password="pass@1234*", is_verified=False)
    return user


@pytest.mark.django_db
class TestAccount:
    # def test_account_registration_url(self, api_client: APIClient):
    #     url = reverse("Account:API:token-registeration")
    #     data = {
    #         "email": "test@example.com",
    #         "password": "pass@1234*",
    #         "password1": "pass@1234*",
    #     }
    #     response: Response = api_client.post(url, data=data)
    #     assert response.status_code == status.HTTP_201_CREATED
    #     assert response.data["email"] == data["email"]
    #     assert "token" in response.data

    def test_account_login_url(self, api_client: APIClient, verified_user: User):
        url = reverse("Account:API:token-login")
        data = {"email": "test@example.com", "password": "pass@1234*"}
        response: Response = api_client.post(url, data=data)
        assert response.status_code == status.HTTP_200_OK
        assert "token" in response.data

    def test_account_unauthenticated_logout_url(self, api_client: APIClient):
        url = reverse("Account:API:token-logout")
        response = api_client.post(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_account_authenticated_logout_url(self, api_client: APIClient, verified_user: User):
        url = reverse("Account:API:token-logout")
        api_client.force_login(user=verified_user)
        Token.objects.get_or_create(user=verified_user)
        response = api_client.post(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_jwt_create_url(self, api_client: APIClient, verified_user: User):
        url = reverse("Account:API:jwt-create")
        data = {"email": "test@example.com", "password": "pass@1234*"}
        response = api_client.post(url, data=data)
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert "email" in response.data
        assert "user_id" in response.data

    def test_change_password_url(self, api_client: APIClient, verified_user: User):
        api_client.force_login(user=verified_user)
        url = reverse("Account:API:change-password")
        data = {
            "old_password": "pass@1234*",
            "new_password": "new_pass@1234*",
            "new_password1": "new_pass@1234*",
        }
        response = api_client.post(url, data=data)
        assert response.status_code == status.HTTP_200_OK

        url = reverse("Account:API:token-login")
        data = {"email": "test@example.com", "password": "new_pass@1234*"}
        response = api_client.post(url, data=data)
        assert response.status_code == status.HTTP_200_OK

    def test_email_does_not_exist_reset_password_url(self, api_client: APIClient):
        url = reverse("Account:API:reset-password")
        data = {"email": "test@example.com"}
        response: Response = api_client.post(url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    # def test_reset_password_url(self, api_client: APIClient, verified_user: User):
    #     url = reverse("Account:API:reset-password")
    #     data = {"email": "test@example.com"}
    #     response: Response = api_client.post(url, data=data)
    #     assert response.status_code == status.HTTP_200_OK

    def test_email_does_not_verification_resend_url(self, api_client: APIClient):
        url = reverse("Account:API:verification-resend")
        data = {"email": "test@example.com"}
        response: Response = api_client.post(url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    # def test_verification_resend_url(self, api_client: APIClient, unverified_user: User):
    #     url = reverse("Account:API:verification-resend")
    #     data = {"email": "test@example.com"}
    #     response: Response = api_client.post(url, data=data)
    #     assert response.status_code == status.HTTP_200_OK
