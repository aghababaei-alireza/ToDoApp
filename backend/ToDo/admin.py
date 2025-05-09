from django.contrib import admin
from .models import Task


class TaskAdmin(admin.ModelAdmin):
    exclude = ('user',)

    def save_model(self, request, obj, form, change):
        if not change or not obj.user_id:
            obj.user = request.user
        super().save_model(request, obj, form, change)


admin.site.register(Task, TaskAdmin)
