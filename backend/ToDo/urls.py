from django.urls import path
from .views import TaskListView, TaskCompleteView, TaskRestoreView, TaskCreateView, TaskUpdateView, TaskDeleteView

app_name = 'ToDo'

urlpatterns = [
    path('', TaskListView.as_view(), name='tasks'),
    path('complete/<int:pk>/', TaskCompleteView.as_view(), name='task_complete'),
    path('restore/<int:pk>/', TaskRestoreView.as_view(), name='task_restore'),
    path('create/', TaskCreateView.as_view(), name='task_create'),
    path('update/<int:pk>/', TaskUpdateView.as_view(), name='task_update'),
    path('delete/<int:pk>/', TaskDeleteView.as_view(), name='task_delete'),
]
