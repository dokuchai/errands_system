from abc import ABC

from django.db.models import F
from rest_framework import serializers

from users.models import CustomUser
from .models import Boards, Tasks, Icons, FriendBoardPermission
from .services import add_new_user


class IconSerializer(serializers.ModelSerializer):
    class Meta:
        model = Icons
        fields = ('id', 'image', 'description')


class BoardFriendSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='friend.id')
    first_name = serializers.CharField(source="friend.first_name")
    last_name = serializers.CharField(source="friend.last_name")
    full_name = serializers.SerializerMethodField('get_full_name')

    class Meta:
        model = FriendBoardPermission
        fields = ('id', 'first_name', 'last_name', 'full_name', 'redactor')

    def get_full_name(self, obj):
        return f'{obj.friend.first_name} {obj.friend.last_name}'


class TaskListSerializer(serializers.ModelSerializer):
    term = serializers.DateTimeField(input_formats=["%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y"], required=False)
    responsible = serializers.SerializerMethodField('get_responsible_name')
    icon = serializers.SerializerMethodField("get_icon_url")
    resp_id = serializers.SerializerMethodField('get_resp_id')

    class Meta:
        model = Tasks
        fields = ('id', 'title', 'status', 'term', 'project', 'responsible', 'icon', 'board', 'resp_id')

    def get_icon_url(self, obj):
        if obj.icon:
            return obj.icon.image.url

    def get_responsible_name(self, obj):
        if obj.responsible:
            return f'{obj.responsible.first_name} {obj.responsible.last_name}'

    def get_resp_id(self, obj):
        if obj.responsible:
            return obj.responsible.id


class TaskDetailSerializer(serializers.ModelSerializer):
    term = serializers.DateTimeField(input_formats=["%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y"], allow_null=True)
    responsible = serializers.SerializerMethodField('get_responsible_name')
    icon = serializers.SerializerMethodField('get_icon_description')
    resp_id = serializers.SerializerMethodField('get_resp_id')

    class Meta:
        model = Tasks
        fields = ('id', 'title', 'text', 'project', 'term', 'responsible', 'icon', 'status', 'resp_id')

    def get_responsible_name(self, obj):
        if obj.responsible:
            return f'{obj.responsible.first_name} {obj.responsible.last_name}'

    def get_icon_description(self, obj):
        if obj.icon:
            return obj.icon.description

    def get_resp_id(self, obj):
        if obj.responsible:
            return obj.responsible.id


class TaskUpdateSerializer(serializers.ModelSerializer):
    term = serializers.DateTimeField(input_formats=["%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y"], allow_null=True,
                                     required=False)
    icon = serializers.CharField(source='icon.description', allow_null=True, required=False)
    first_name = serializers.CharField(default='')
    last_name = serializers.CharField(default='')

    class Meta:
        model = Tasks
        fields = ('id', 'title', 'text', 'project', 'term', 'responsible', 'icon', 'status', 'first_name', 'last_name')

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.text = validated_data.get('text', instance.text)
        instance.project = validated_data.get('project', instance.project)
        instance.term = validated_data.get('term', instance.term)
        instance.status = validated_data.get('status', instance.status)
        icon, responsible = validated_data.pop('icon', None), validated_data.pop('responsible', None)
        try:
            instance.icon = Icons.objects.get(description=icon['description'])
        except Icons.DoesNotExist:
            instance.icon = None
        except TypeError:
            pass
        try:
            responsible_name = str(responsible).split(' ')
            instance.responsible = CustomUser.objects.get(first_name=responsible_name[0],
                                                          last_name=responsible_name[1])
        except CustomUser.DoesNotExist:
            instance.responsible = None
        except (TypeError, IndexError):
            pass
        if 'first_name' in validated_data and 'last_name' in validated_data:
            add_new_user(first_name=validated_data['first_name'], last_name=validated_data['last_name'],
                         pk=instance.board.id, task=instance)
        instance.save()
        return instance


class BoardSerializer(serializers.ModelSerializer):
    tasks = TaskListSerializer(many=True)

    class Meta:
        model = Boards
        fields = ('id', 'title', 'tasks')


class BoardBaseSerializer(serializers.BaseSerializer, ABC):
    def to_representation(self, instance):
        projects = Tasks.objects.filter(board=instance).exclude(project="").distinct().values("project")
        [project.update(
            {"tasks": TaskListSerializer(Tasks.objects.filter(project=project["project"]).order_by('-id'), many=True,
                                         read_only=True).data}) for project in projects]
        tasks = Tasks.objects.filter(board=instance, project="").order_by('-id').values('id', 'title', 'status', 'term',
                                                                                        'icon', 'board', 'responsible',
                                                                                        resp_id=F('responsible_id'))
        [task.update({"responsible":
                          BoardFriendSerializer(FriendBoardPermission.objects.get(friend_id=task['responsible'])).data[
                              'full_name']}) for task in tasks if task['responsible']]
        [task.update(
            {"icon": IconSerializer(Icons.objects.get(id=task['icon'])).data['image']}) for
            task in tasks if task['icon']]
        return {
            "id": instance.id,
            "title": instance.title,
            "projects": [project for project in projects],
            "tasks": [task for task in tasks]
        }
