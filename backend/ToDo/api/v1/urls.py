from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import TasksViewSet, WeatherAPIView

router = DefaultRouter()
router.register(r"tasks", TasksViewSet, basename="tasks")

urlpatterns = [
    path("weather/", WeatherAPIView.as_view(), name="weather-api"),
]

urlpatterns += router.urls
