from rest_framework import serializers
from .models import ChangeLog


class ChangeLogSerializer(serializers.ModelSerializer):
    data = serializers.SerializerMethodField('get_readable_data')
    action = serializers.CharField(source='action_on_model')

    class Meta:
        model = ChangeLog
        fields = ('id', 'changed', 'user', 'action', 'data')

    def get_readable_data(self, obj):
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
        return data
