from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "due_date"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
            "due_date": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            ),
        }
        error_messages = {
            "title": {
                "required": "This field is required.",
                "max_length": "Title cannot exceed 400 characters.",
            },
            "description": {
                "max_length": "Description cannot exceed 1000 characters."
            },
            "due_date": {"invalid": "Enter a valid date/time."},
        }
