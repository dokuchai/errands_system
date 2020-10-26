from abc import ABC

from django.db.models import F
from rest_framework import serializers

from users.models import CustomUser
from .models import Boards, Tasks, Icons, FriendBoardPermission, Project
from .services import add_new_responsible, add_new_user


class IconSerializer(serializers.ModelSerializer):
    class Meta:
        model = Icons
        fields = ('id', 'image', 'description')


class SoExecutorSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField('get_full_name')

    class Meta:
        model = CustomUser
        fields = ('id', 'full_name')

    def get_full_name(self, obj):
        return f'{obj.last_name} {obj.first_name}'


class BoardFriendSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='friend.id')
    first_name = serializers.CharField(source="friend.first_name")
    last_name = serializers.CharField(source="friend.last_name")
    full_name = serializers.SerializerMethodField('get_full_name')

    class Meta:
        model = FriendBoardPermission
        fields = ('id', 'first_name', 'last_name', 'full_name', 'redactor')

    def get_full_name(self, obj):
        return f'{obj.friend.last_name} {obj.friend.first_name}'


class TaskCreateSerializer(serializers.ModelSerializer):
    term = serializers.DateTimeField(input_formats=["%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y"], required=False)
    icon = serializers.SerializerMethodField("get_icon_url")
    so_executors = SoExecutorSerializer(many=True, read_only=True)
    project = serializers.CharField(default='', required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Tasks
        fields = ('id', 'title', 'status', 'term', 'project', 'responsible', 'icon', 'board', 'so_executors')

    def get_icon_url(self, obj):
        if obj.icon:
            return obj.icon.image.url


class TaskListSerializer(serializers.ModelSerializer):
    term = serializers.DateTimeField(input_formats=["%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y"], required=False)
    responsible = serializers.SerializerMethodField('get_responsible_name')
    icon = serializers.SerializerMethodField("get_icon_url")
    resp_id = serializers.SerializerMethodField('get_resp_id')
    so_executors = SoExecutorSerializer(many=True, read_only=True)
    project = serializers.SerializerMethodField('get_project')

    class Meta:
        model = Tasks
        fields = ('id', 'title', 'status', 'term', 'project', 'responsible', 'icon', 'board', 'resp_id', 'so_executors')

    def get_icon_url(self, obj):
        if obj.icon:
            return obj.icon.image.url

    def get_responsible_name(self, obj):
        if obj.responsible:
            return f'{obj.responsible.last_name} {obj.responsible.first_name}'

    def get_resp_id(self, obj):
        if obj.responsible:
            return obj.responsible.id

    def get_project(self, obj):
        if obj.project:
            return obj.project.title


class TaskListWithoutProjectSerializer(serializers.ModelSerializer):
    term = serializers.DateTimeField(input_formats=["%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y"], required=False)
    responsible = serializers.SerializerMethodField('get_responsible_name')
    icon = serializers.SerializerMethodField("get_icon_url")
    resp_id = serializers.SerializerMethodField('get_resp_id')
    so_executors = SoExecutorSerializer(many=True, read_only=True)

    class Meta:
        model = Tasks
        fields = ('id', 'title', 'status', 'term', 'responsible', 'icon', 'board', 'resp_id', 'so_executors')

    def get_icon_url(self, obj):
        if obj.icon:
            return obj.icon.image.url

    def get_responsible_name(self, obj):
        if obj.responsible:
            return f'{obj.responsible.last_name} {obj.responsible.first_name}'

    def get_resp_id(self, obj):
        if obj.responsible:
            return obj.responsible.id


class TaskDetailSerializer(serializers.ModelSerializer):
    term = serializers.DateTimeField(input_formats=["%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y"], allow_null=True)
    responsible = serializers.SerializerMethodField('get_responsible_name')
    icon = serializers.SerializerMethodField('get_icon_description')
    resp_id = serializers.SerializerMethodField('get_resp_id')
    so_executors = SoExecutorSerializer(many=True, read_only=True)
    project = serializers.SerializerMethodField('get_project')

    class Meta:
        model = Tasks
        fields = ('id', 'title', 'text', 'project', 'term', 'responsible', 'icon', 'status', 'resp_id', 'so_executors')

    def get_responsible_name(self, obj):
        if obj.responsible:
            return f'{obj.responsible.last_name} {obj.responsible.first_name}'

    def get_icon_description(self, obj):
        if obj.icon:
            return obj.icon.description

    def get_resp_id(self, obj):
        if obj.responsible:
            return obj.responsible.id

    def get_project(self, obj):
        if obj.project:
            return obj.project.title


class TaskUpdateSerializer(serializers.ModelSerializer):
    term = serializers.DateTimeField(input_formats=["%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y"], allow_null=True,
                                     required=False)
    icon = serializers.CharField(source='icon.description', allow_null=True, required=False)
    so_executors = SoExecutorSerializer(many=True, read_only=True)
    name = serializers.CharField(default='', allow_null=True, allow_blank=True)
    responsible = serializers.SerializerMethodField('get_responsible_name')
    resp_id = serializers.CharField(default='')
    project = serializers.CharField(default='')
    exec_id = serializers.ListField(default=[])
    exec_name = serializers.ListField(default=[])

    class Meta:
        model = Tasks
        fields = (
            'id', 'title', 'text', 'project', 'term', 'responsible', 'icon', 'status', 'name', 'so_executors',
            'resp_id', 'exec_id', 'exec_name')

    def get_responsible_name(self, obj):
        if obj.responsible:
            return f'{obj.responsible.last_name} {obj.responsible.first_name}'.lstrip()

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.text = validated_data.get('text', instance.text)
        instance.term = validated_data.get('term', instance.term)
        instance.status = validated_data.get('status', instance.status)
        icon, executors = validated_data.pop('icon', None), []
        try:
            instance.icon = Icons.objects.get(description=icon['description'])
        except Icons.DoesNotExist:
            instance.icon = None
        except TypeError:
            pass
        if 'resp_id' in validated_data:
            if str(validated_data['resp_id']).isdigit():
                try:
                    instance.responsible = CustomUser.objects.get(id=int(validated_data['resp_id']))
                except CustomUser.DoesNotExist:
                    pass
            else:
                instance.responsible = None
        if 'name' in validated_data:
            responsible = None
            name = str(validated_data['name']).split(' ')
            if len(name) == 2:
                try:
                    responsible = CustomUser.objects.get(first_name=name[1], last_name=name[0],
                                                         friend_board=instance.board)
                except CustomUser.DoesNotExist:
                    responsible = add_new_responsible(first_name=name[1], last_name=name[0], board_id=instance.board.id)
            elif len(name) == 1 and name[0] != '':
                try:
                    responsible = CustomUser.objects.get(first_name=name[0], last_name='', friend_board=instance.board)
                except CustomUser.DoesNotExist:
                    responsible = add_new_responsible(first_name=name[0], last_name='', board_id=instance.board.id)
            instance.responsible = responsible
        if 'project' in validated_data:
            project, created = Project.objects.get_or_create(title=validated_data['project'])
            instance.project = project
        if 'exec_name' in validated_data:
            for executor in validated_data['exec_name']:
                name = executor.split(' ')
                if len(name) == 1:
                    executors.append(add_new_user(first_name=name[1], last_name='', board_id=instance.board.id))
                elif len(name) == 2:
                    executors.append(add_new_user(first_name=name[1], last_name=name[0], board_id=instance.board.id))
        if 'exec_id' in validated_data:
            for executor in validated_data['exec_id']:
                executors.append(CustomUser.objects.get(id=executor))
        instance.so_executors.add(*executors)
        instance.save()
        return instance


class ProjectsSerializer(serializers.ModelSerializer):
    project = serializers.CharField(source='title')
    tasks = TaskListSerializer(many=True, source='project_tasks')

    class Meta:
        model = Project
        fields = ('project', 'tasks')


class ProjectsWithActiveTasksSerializer(serializers.ModelSerializer):
    project = serializers.CharField(source='title')
    tasks = serializers.SerializerMethodField('get_active_tasks')

    class Meta:
        model = Project
        fields = ('project', 'tasks')

    def get_active_tasks(self, obj):
        tasks = Tasks.objects.filter(project=obj, status__in=('В работе', 'Требуется помощь'))
        return TaskListSerializer(tasks, many=True).data


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Boards
        fields = ('id', 'title',)


class BoardBaseSerializer(serializers.BaseSerializer, ABC):
    def to_representation(self, instance):
        projects = Project.objects.filter(project_tasks__board_id=instance.id).distinct()
        tasks = Tasks.objects.filter(board=instance, project=None).order_by('-id').annotate(resp_id=F('responsible_id'))
        return {
            "id": instance.id,
            "title": instance.title,
            "projects": ProjectsSerializer(projects, many=True).data,
            "tasks": TaskListWithoutProjectSerializer(tasks, many=True).data
        }


class BoardActiveTasksSerializer(serializers.BaseSerializer, ABC):
    def to_representation(self, instance):
        projects = Project.objects.filter(project_tasks__board_id=instance.id,
                                          project_tasks__status__in=('В работе', 'Требуется помощь')).distinct()
        tasks = Tasks.objects.filter(board=instance, project=None,
                                     status__in=('В работе', 'Требуется помощь')).order_by('-id').annotate(
            resp_id=F('responsible_id'))
        return {
            "id": instance.id,
            "title": instance.title,
            "projects": ProjectsWithActiveTasksSerializer(projects, many=True).data,
            "tasks": TaskListWithoutProjectSerializer(tasks, many=True).data
        }
