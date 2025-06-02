import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.response import Response
from Account.models import User
from rest_framework.authtoken.models import Token
from ToDo.models import Task


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def verified_user():
    user = User.objects.create_user(
        email="test@example.com",
        password="pass@1234*",
        is_verified=True
    )
    return user


@pytest.fixture
def unverified_user() -> User:
    user = User.objects.create_user(
        email="test@example.com",
        password="pass@1234*",
        is_verified=False
    )
    return user


@pytest.fixture
def incompleted_task(verified_user: User) -> Task:
    return Task.objects.create(
        title="Sample Task",
        description="This is a sample task.",
        due_date="2023-12-31T23:59:59Z",
        user=verified_user
    )


@pytest.fixture
def completed_task(verified_user: User) -> Task:
    return Task.objects.create(
        title="Sample Task",
        description="This is a sample task.",
        due_date="2023-12-31T23:59:59Z",
        completed=True,
        user=verified_user
    )


@pytest.mark.django_db
class TestTask:
    def test_task_list_requires_authentication(self, api_client: APIClient):
        url = reverse('ToDo:tasks-list')
        response: Response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_task_list_authenticated_verified_user(self, api_client: APIClient, verified_user: User):
        url = reverse('ToDo:tasks-list')
        api_client.force_authenticate(user=verified_user)
        response: Response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_task_list_authenticated_unverified_user(self, api_client: APIClient, unverified_user: User):
        url = reverse('ToDo:tasks-list')
        api_client.force_authenticate(user=unverified_user)
        response: Response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_task_create_authenticated_verified_user(self, api_client: APIClient, verified_user: User):
        url = reverse('ToDo:tasks-list')
        api_client.force_authenticate(user=verified_user)
        data = {"title": "Test Task", "description": "Test Description",
                "due_date": "2023-12-31T23:59:59Z"}
        response: Response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == data['title']
        assert response.data['description'] == data['description']
        assert response.data['due_date'] == data['due_date']

    def test_task_create_incompleted_data(self, api_client: APIClient, verified_user: User):
        url = reverse('ToDo:tasks-list')
        api_client.force_authenticate(user=verified_user)
        data = {"description": "Test Description",
                "due_date": "2023-12-31T23:59:59Z"}
        response: Response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_task_create_authenticated_unverified_user(self, api_client: APIClient, unverified_user: User):
        url = reverse('ToDo:tasks-list')
        api_client.force_authenticate(user=unverified_user)
        data = {"title": "Test Task", "description": "Test Description"}
        response: Response = api_client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_task_detail_requires_authentication(self, api_client: APIClient, incompleted_task: Task):
        url = reverse('ToDo:tasks-detail', args=[incompleted_task.id])
        response: Response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_task_detail_authenticated_verified_user(self, api_client: APIClient, incompleted_task: Task):
        url = reverse('ToDo:tasks-detail', args=[incompleted_task.id])
        api_client.force_authenticate(user=incompleted_task.user)
        response: Response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == incompleted_task.id
        assert response.data['title'] == incompleted_task.title
        assert response.data['description'] == incompleted_task.description
        assert response.data['due_date'] == incompleted_task.due_date
        assert response.data['completed'] == incompleted_task.completed

    def test_task_detail_authenticated_unverified_user(self, api_client: APIClient, incompleted_task: Task):
        url = reverse('ToDo:tasks-detail', args=[incompleted_task.id])
        user = incompleted_task.user
        user.is_verified = False
        api_client.force_authenticate(user=user)
        response: Response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_task_update_requires_authentication(self, api_client: APIClient, incompleted_task: Task):
        url = reverse('ToDo:tasks-detail', args=[incompleted_task.id])
        data = {"title": "Updated Task", "description": "Updated Desc"}
        response: Response = api_client.put(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_task_update_authenticated_verified_user(self, api_client: APIClient, incompleted_task: Task):
        url = reverse('ToDo:tasks-detail', args=[incompleted_task.id])
        api_client.force_authenticate(user=incompleted_task.user)
        data = {"title": "Updated Task", "description": "Updated Desc"}
        response: Response = api_client.put(url, data)
        assert response.status_code == status.HTTP_200_OK

    def test_task_update_authenticated_verified_user_incompleted_data(self, api_client: APIClient, incompleted_task: Task):
        url = reverse('ToDo:tasks-detail', args=[incompleted_task.id])
        api_client.force_authenticate(user=incompleted_task.user)
        data = {"description": "Updated Desc"}
        response: Response = api_client.put(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_task_update_authenticated_unverified_user(self, api_client: APIClient, incompleted_task: Task):
        url = reverse('ToDo:tasks-detail', args=[incompleted_task.id])
        user = incompleted_task.user
        user.is_verified = False
        api_client.force_authenticate(user=user)
        data = {"title": "Updated Task", "description": "Updated Desc"}
        response: Response = api_client.put(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_task_partial_update_requires_authentication(self, api_client: APIClient, incompleted_task: Task):
        url = reverse('ToDo:tasks-detail', args=[incompleted_task.id])
        data = {"title": "Updated Task"}
        response: Response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_task_partial_update_authenticated_verified_user(self, api_client: APIClient, incompleted_task: Task):
        url = reverse('ToDo:tasks-detail', args=[incompleted_task.id])
        api_client.force_authenticate(user=incompleted_task.user)
        data = {"title": "Updated Task"}
        response: Response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK

    def test_task_partial_update_authenticated_unverified_user(self, api_client: APIClient, incompleted_task: Task):
        url = reverse('ToDo:tasks-detail', args=[incompleted_task.id])
        user = incompleted_task.user
        user.is_verified = False
        api_client.force_authenticate(user=user)
        data = {"title": "Updated Task"}
        response: Response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_task_delete_requires_authentication(self, api_client: APIClient, incompleted_task: Task):
        url = reverse('ToDo:tasks-detail', args=[incompleted_task.id])
        response: Response = api_client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_task_delete_authenticated_verified_user(self, api_client: APIClient, incompleted_task: Task):
        url = reverse('ToDo:tasks-detail', args=[incompleted_task.id])
        api_client.force_authenticate(user=incompleted_task.user)
        response: Response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_task_delete_authenticated_unverified_user(self, api_client: APIClient, incompleted_task: Task):
        url = reverse('ToDo:tasks-detail', args=[incompleted_task.id])
        user = incompleted_task.user
        user.is_verified = False
        api_client.force_authenticate(user=user)
        response: Response = api_client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_task_complete_requires_authentication(self, api_client: APIClient, incompleted_task: Task):
        url = reverse('ToDo:tasks-tasks-complete', args=[incompleted_task.id])
        response: Response = api_client.patch(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_task_complete_authenticated_verified_user(self, api_client: APIClient, incompleted_task: Task):
        url = reverse('ToDo:tasks-tasks-complete', args=[incompleted_task.id])
        api_client.force_authenticate(user=incompleted_task.user)
        response: Response = api_client.patch(url)
        assert response.status_code == status.HTTP_200_OK
        incompleted_task.refresh_from_db()
        assert incompleted_task.completed is True

    def test_task_complete_authenticated_unverified_user(self, api_client: APIClient, incompleted_task: Task):
        url = reverse('ToDo:tasks-tasks-complete', args=[incompleted_task.id])
        user = incompleted_task.user
        user.is_verified = False
        api_client.force_authenticate(user=user)
        response: Response = api_client.patch(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_task_complete_already_completed(self, api_client: APIClient, completed_task: Task):
        url = reverse('ToDo:tasks-tasks-complete', args=[completed_task.id])
        api_client.force_authenticate(user=completed_task.user)
        response: Response = api_client.patch(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['detail'] == "Task is already completed."

    def test_task_restore_requires_authentication(self, api_client: APIClient, completed_task: Task):
        url = reverse('ToDo:tasks-tasks-restore', args=[completed_task.id])
        response: Response = api_client.patch(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_task_restore_authenticated_verified_user(self, api_client: APIClient, completed_task: Task):
        url = reverse('ToDo:tasks-tasks-restore', args=[completed_task.id])
        api_client.force_authenticate(user=completed_task.user)
        response: Response = api_client.patch(url)
        assert response.status_code == status.HTTP_200_OK
        completed_task.refresh_from_db()
        assert completed_task.completed is False

    def test_task_restore_authenticated_unverified_user(self, api_client: APIClient, completed_task: Task):
        url = reverse('ToDo:tasks-tasks-restore', args=[completed_task.id])
        user = completed_task.user
        user.is_verified = False
        api_client.force_authenticate(user=user)
        response: Response = api_client.patch(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_task_restore_not_completed(self, api_client: APIClient, incompleted_task: Task):
        url = reverse('ToDo:tasks-tasks-restore', args=[incompleted_task.id])
        api_client.force_authenticate(user=incompleted_task.user)
        response: Response = api_client.patch(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['detail'] == "Task is not completed yet."
