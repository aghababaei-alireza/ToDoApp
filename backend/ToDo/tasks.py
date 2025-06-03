from celery import shared_task
from .models import Task


@shared_task
def remove_completed_tasks():
    """
    Remove all completed tasks from the database.
    This task will be scheduled to run every 10 minutes.
    """
    Task.objects.filter(completed=True).delete()
    print("Completed tasks removed successfully.")
