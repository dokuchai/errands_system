from rest_framework import serializers
from .models import CustomUser


class CustomUserSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    father_name = serializers.CharField(required=True)
    subdivision = serializers.CharField(required=True)
    position = serializers.CharField(required=True)


class UserSignInSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


class UserRegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    father_name = serializers.CharField(allow_blank=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    password_confirm = serializers.CharField(required=True)


class UserProfileSerializer(serializers.Serializer):
    email = serializers.EmailField(allow_blank=True, required=False)
    first_name = serializers.CharField(allow_blank=True, required=False)
    last_name = serializers.CharField(allow_blank=True, required=False)
    father_name = serializers.CharField(allow_blank=True, required=False)
    subdivision = serializers.CharField(allow_blank=True, required=False)
    position = serializers.CharField(allow_blank=True, required=False)
    password = serializers.CharField(allow_blank=True, required=False)
    password_confirm = serializers.CharField(allow_blank=True, required=False)
