from django.contrib.auth import authenticate
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from errands.services import password_reset
from .serializers import UserSignInSerializer, UserRegisterSerializer, UserProfileSerializer, CustomUserSerializer
from .models import CustomUser
from .services import token_stuff, user_partial_update


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
            return Response({'detail': 'Неверные данные для входа!'}, status=HTTP_404_NOT_FOUND)
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
        user = CustomUser.objects.create(email=register_serializer.data['email'],
                                         first_name=register_serializer.data['first_name'],
                                         last_name=register_serializer.data['last_name'],
                                         father_name=register_serializer.data['father_name'])
        user.set_password(register_serializer.data['password'])
        user.save()
        return token_stuff(user=user)


class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        return Response(password_reset(email=email), status=HTTP_200_OK)


class ProfileUserView(APIView):
    @staticmethod
    def get(request):
        try:
            return Response(CustomUserSerializer(CustomUser.objects.get(id=request.user.id)).data)
        except CustomUser.DoesNotExist:
            return Response({'message': 'Пользователя не существует'}, status=HTTP_404_NOT_FOUND)

    @staticmethod
    def post(request):
        profile_serializer = UserProfileSerializer(data=request.data)
        if not profile_serializer.is_valid():
            return Response(profile_serializer.errors, status=HTTP_400_BAD_REQUEST)
        if profile_serializer.data['password'] != profile_serializer.data['password_confirm']:
            return Response({'message': 'Пароли не совпадают!'}, status=HTTP_400_BAD_REQUEST)
        user = CustomUser.objects.get(id=request.user.id)
        user_partial_update(request=request, serializer=profile_serializer)
        return Response(CustomUserSerializer(user).data, status=HTTP_200_OK)
