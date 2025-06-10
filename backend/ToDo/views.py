from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError, PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .models import Task
from .forms import TaskForm
from Account.mixins import VerifiedUserRequiredMixin


class IndexView(TemplateView):
    template_name = "ToDo/index.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("ToDo:tasks")
        return super().get(request, *args, **kwargs)


class TaskListView(LoginRequiredMixin, VerifiedUserRequiredMixin, ListView):
    model = Task
    template_name = "ToDo/task_list.html"
    context_object_name = "tasks"
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)
        status = self.request.GET.get("status", "")
        if status == "completed":
            queryset = queryset.filter(completed=True)
        elif status == "active":
            queryset = queryset.filter(completed=False)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        status = self.request.GET.get("status", "")
        context["status"] = status
        return context


class TaskCompleteView(LoginRequiredMixin, VerifiedUserRequiredMixin, View):
    def post(self, request, pk: int):
        try:
            task = Task.objects.get(user=request.user, pk=pk)
        except Task.DoesNotExist:
            return render(request, "404.html")

        if task.completed:
            raise ValidationError("Task is already completed.")

        task.completed = True
        task.save()
        return redirect("ToDo:tasks")


class TaskRestoreView(LoginRequiredMixin, VerifiedUserRequiredMixin, View):
    def post(self, request, pk: int):
        try:
            task = Task.objects.get(user=request.user, pk=pk)
        except Task.DoesNotExist:
            return render(request, "404.html")

        if not task.completed:
            raise ValidationError("Task is not completed.")

        task.completed = False
        task.save()
        return redirect("ToDo:tasks")


class TaskCreateView(LoginRequiredMixin, VerifiedUserRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "ToDo/task_form.html"
    success_url = reverse_lazy("ToDo:tasks")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "New Task"
        context["form_button"] = "Create"
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        return render(self.request, self.template_name, {"form": form})


class TaskUpdateView(LoginRequiredMixin, VerifiedUserRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "ToDo/task_form.html"
    success_url = reverse_lazy("ToDo:tasks")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "Update Task"
        context["form_button"] = "Update"
        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied(
                "You do not have permission to edit this task.")
        return obj

    def form_invalid(self, form):
        return render(self.request, self.template_name, {"form": form})


class TaskDeleteView(LoginRequiredMixin, VerifiedUserRequiredMixin, DeleteView):
    model = Task
    success_url = reverse_lazy("ToDo:tasks")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise ValidationError(
                "You do not have permission to delete this task.")
        return obj
