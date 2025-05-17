from rest_framework import serializers
from ToDo.models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'user', 'title', 'description', 'due_date',
                  'completed', 'created_at', 'updated_at']
        read_only_fields = ['user', 'completed', 'craeted_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
