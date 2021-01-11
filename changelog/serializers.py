from rest_framework import serializers
from .models import ChangeLog


class ChangeLogSerializer(serializers.ModelSerializer):
    data = serializers.SerializerMethodField('get_readable_data')
    action = serializers.CharField(source='action_on_model')
    user = serializers.SerializerMethodField('get_user_full_name')

    class Meta:
        model = ChangeLog
        fields = ('id', 'changed', 'user', 'action', 'data')

    @staticmethod
    def get_user_full_name(obj):
        return f'{obj.user}'

    @staticmethod
    def get_readable_data(obj):
        data = obj.data
        if 'responsible' in data:
            responsible = data['responsible']
            if responsible:
                user = str(data['responsible']).lstrip('<CustomUser: ').rstrip('>')
                data.update({'responsible': user})
        if 'icon' in data:
            icon = data['icon']
            if icon:
                icon = str(data['icon']).lstrip('<Icons: ').rstrip('>')
                data.update({'icon': icon})
        if 'project' in data:
            project = data['project']
            if project:
                project = str(data['project']).lstrip('<Project: ').rstrip('>')
                data.update({'project': project})
        if 'board' in data:
            board = data['board']
            if board:
                board = str(data['board']).lstrip('<Boards: ').rstrip('>')
                data.update({'board': board})
        if 'so_executors' in data:
            so_executors = data['so_executors']
            if so_executors:
                so_executors = [
                    {'full_name': str(so_executor).lstrip('<CustomUser: ').rstrip('>')} for so_executor in so_executors]
            data.update({'so_executors': so_executors})
        return data
