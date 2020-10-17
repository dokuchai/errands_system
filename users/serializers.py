from rest_framework import serializers

from users.models import CustomUser


class CustomUserSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    father_name = serializers.CharField(required=True)
    subdivision = serializers.CharField(required=True)
    position = serializers.CharField(required=True)


class UserSignInSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class NewUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'first_name', "last_name")
