from rest_framework import serializers
from .models import Boards, Tasks


class TaskListSerializer(serializers.ModelSerializer):
    term = serializers.DateTimeField(input_formats=["%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y"], required=False)

    class Meta:
        model = Tasks
        fields = ('id', 'title', 'status', 'term', 'project', 'responsible', 'icon', 'board')


class TaskDetailSerializer(serializers.ModelSerializer):
    term = serializers.DateTimeField(input_formats=["%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y"])

    class Meta:
        model = Tasks
        fields = ('id', 'title', 'text', 'project', 'term', 'responsible', 'icon', 'status')


class BoardSerializer(serializers.ModelSerializer):
    tasks = TaskListSerializer(many=True)

    class Meta:
        model = Boards
        fields = ('id', 'title', 'tasks')
