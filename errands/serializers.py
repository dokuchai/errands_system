from rest_framework.serializers import ModelSerializer
from .models import Boards


class BoardSerializer(ModelSerializer):
    class Meta:
        model = Boards
        fields = ('title',)