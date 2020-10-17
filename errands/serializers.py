from abc import ABC

from django.db.models import Value, CharField, F
from rest_framework import serializers
from .models import Boards, Tasks


class TaskListSerializer(serializers.ModelSerializer):
    term = serializers.DateTimeField(input_formats=["%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y"], required=False)
    # responsible = serializers.CharField(source='responsible.get_full_name')

    class Meta:
        model = Tasks
        fields = ('id', 'title', 'status', 'term', 'project', 'responsible', 'icon', 'board')


class TaskDetailSerializer(serializers.ModelSerializer):
    term = serializers.DateTimeField(input_formats=["%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y"], allow_null=True)
    # responsible = serializers.CharField(source='responsible.get_full_name')

    class Meta:
        model = Tasks
        fields = ('id', 'title', 'text', 'project', 'term', 'responsible', 'icon', 'status')

    # def responsible_name(self):


class BoardSerializer(serializers.ModelSerializer):
    tasks = TaskListSerializer(many=True)

    class Meta:
        model = Boards
        fields = ('id', 'title', 'tasks')


class BoardBaseSerializer(serializers.BaseSerializer, ABC):
    def to_representation(self, instance):
        projects = Tasks.objects.filter(board=instance).exclude(project="").distinct().values("project")
        [project.update({"tasks": TaskListSerializer(Tasks.objects.filter(project=project["project"]), many=True,
                                                     read_only=True).data}) for project in projects]
        return {
            "id": instance.id,
            "title": instance.title,
            "projects": [project for project in projects],
            "tasks": Tasks.objects.filter(board=instance, project="").values('id', 'title', 'status', 'term',
                                                                             'icon', 'board', 'responsible')
        }
