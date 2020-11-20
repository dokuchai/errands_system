from django.contrib.auth import authenticate
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSignInSerializer, UserRegisterSerializer
from .models import CustomUser
from .services import token_stuff


class CustomUserTokenCreateOrRefresh(APIView):
    @staticmethod
    def post(request):
        sign_in_serializer = UserSignInSerializer(data=request.data)
        if not sign_in_serializer.is_valid():
            return Response(sign_in_serializer.errors, status=HTTP_400_BAD_REQUEST)
        user = authenticate(
            email=sign_in_serializer.data['email'],
            password=sign_in_serializer.data['password']
        )
        if not user:
            return Response({'detail': 'Invalid Credentials or activate account'}, status=HTTP_404_NOT_FOUND)
        return token_stuff(user=user)


class RegisterUserView(APIView):
    @staticmethod
    def post(request):
        register_serializer = UserRegisterSerializer(data=request.data)
        if not register_serializer.is_valid():
            return Response(register_serializer.errors, status=HTTP_400_BAD_REQUEST)
        if CustomUser.objects.filter(email=register_serializer.data['email']):
            return Response({'message': 'Пользователь с таким email уже зарегистрирован!'}, status=HTTP_400_BAD_REQUEST)
        if register_serializer.data['password'] != register_serializer.data['password_confirm']:
            return Response({'message': 'Пароли не совпадают!'}, status=HTTP_400_BAD_REQUEST)
        user = CustomUser.objects.create(email=register_serializer.data['email'])
        user.set_password(register_serializer.data['password'])
        user.save()
        return token_stuff(user=user)
