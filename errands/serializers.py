from abc import ABC
from rest_framework import serializers

from users.models import CustomUser
from .models import Boards, Tasks, Icons
from users.serializers import NewUserSerializer


class IconSerializer(serializers.ModelSerializer):
    class Meta:
        model = Icons
        fields = ('id', 'image', 'description')


class TaskListSerializer(serializers.ModelSerializer):
    term = serializers.DateTimeField(input_formats=["%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y"], required=False)
    icon = serializers.SerializerMethodField("get_icon_url")

    class Meta:
        model = Tasks
        fields = ('id', 'title', 'status', 'term', 'project', 'responsible', 'icon', 'board')

    def get_icon_url(self, obj):
        if obj.icon:
            return obj.icon.image.url


class TaskDetailSerializer(serializers.ModelSerializer):
    term = serializers.DateTimeField(input_formats=["%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y"], allow_null=True)
    responsible = serializers.SerializerMethodField('get_responsible_name')
    icon = serializers.CharField(source="icon.description")

    class Meta:
        model = Tasks
        fields = ('id', 'title', 'text', 'project', 'term', 'responsible', 'icon', 'status')

    def get_responsible_name(self, obj):
        if obj.responsible:
            return f'{obj.responsible.first_name} {obj.responsible.last_name}'


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
        tasks = Tasks.objects.filter(board=instance, project="").values('id', 'title', 'status', 'term',
                                                                        'icon', 'board', 'responsible')
        [task.update(
            {"responsible": NewUserSerializer(CustomUser.objects.get(id=task['responsible'])).data['full_name']}) for
            task in tasks if task['responsible']]
        [task.update(
            {"icon": IconSerializer(Icons.objects.get(id=task['icon'])).data['image']}) for
            task in tasks if task['icon']]
        return {
            "id": instance.id,
            "title": instance.title,
            "projects": [project for project in projects],
            "tasks": [task for task in tasks]
        }
