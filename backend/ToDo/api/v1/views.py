from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
import requests
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from ToDo.models import Task
from .serializers import TaskSerializer
from .permissions import IsOwner, IsVerified
from .paginations import DefaultPagination


class TasksViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing Task instances.
    """

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsOwner, IsVerified]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["title", "completed", "due_date"]
    search_fields = ["title", "description"]
    ordering_fields = ["due_date"]
    pagination_class = DefaultPagination

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        queryset = queryset.filter(user=self.request.user)
        return queryset

    @action(
        detail=True,
        methods=["PATCH"],
        url_path="complete",
        url_name="tasks-complete",
    )
    def complete_task(self, request, pk=None):
        """
        Mark a task as completed.
        """
        task = self.get_object()
        if task.completed:
            return Response(
                {"detail": "Task is already completed."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        task.completed = True
        task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["PATCH"],
        url_path="restore",
        url_name="tasks-restore",
    )
    def restore_task(self, request, pk=None):
        """
        Mark a task as incompleted.
        """
        task = self.get_object()
        if not task.completed:
            return Response(
                {"detail": "Task is not completed yet."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        task.completed = False
        task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data)


class WeatherAPIView(APIView):
    """
    A simple API view to return weather data.
    """
    @method_decorator(cache_page(60 * 20))
    def get(self, request, *args, **kwargs):
        params = {
            "q": "Isfahan",
            "appid": "6886aff89b6961166d6607b0bf7f699e",
        }
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params=params
        )
        return Response(response.json(), status=response.status_code)
