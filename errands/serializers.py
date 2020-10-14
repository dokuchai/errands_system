from rest_framework import serializers
from .models import Boards, Tasks


class TaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tasks
        fields = ('id', 'title', 'term', 'project', 'responsible', 'icon', 'board')


class TaskDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tasks
        fields = ('id', 'title', 'text', 'project', 'term', 'responsible', 'icon', 'status')


class BoardSerializer(serializers.ModelSerializer):
    tasks = TaskListSerializer(many=True)

    class Meta:
        model = Boards
        fields = ('id', 'title', 'tasks')
