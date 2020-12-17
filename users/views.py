from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND
)
from rest_framework.response import Response
from rest_framework.views import APIView

from errands.services import send_mail_password_reset, reset_user_password
from .serializers import UserSignInSerializer, UserRegisterSerializer, UserProfileSerializer, CustomUserSerializer, \
    UserPasswordRefresh
from .models import CustomUser
from .services import token_stuff, user_partial_update, custom_password_validate


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


class SendMailResetPasswordView(APIView):
    @staticmethod
    def post(request):
        return Response(send_mail_password_reset(email=request.data.get('email')), status=HTTP_200_OK)


class ResetPasswordView(APIView):
    @staticmethod
    def post(request):
        return Response(
            reset_user_password(user_id=request.data.get('user_id'), password=request.data.get('password'),
                                timestamp=request.data.get('timestamp'), signature=request.data.get('signature')),
            status=HTTP_200_OK)


class ProfileUserView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request):
        return Response(CustomUserSerializer(CustomUser.objects.get(id=request.user.id)).data)

    @staticmethod
    def put(request):
        profile_serializer = UserProfileSerializer(data=request.data)
        if not profile_serializer.is_valid():
            return Response(profile_serializer.errors, status=HTTP_400_BAD_REQUEST)
        return Response(CustomUserSerializer(user_partial_update(request, profile_serializer)).data, status=HTTP_200_OK)


class PasswordRefreshView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def post(request):
        password_serializer = UserPasswordRefresh(data=request.data)
        if not password_serializer.is_valid():
            return Response(password_serializer.errors, status=HTTP_400_BAD_REQUEST)
        if password_serializer.data['password'] != password_serializer.data['password_confirm']:
            return Response({'detail': 'Пароли не совпадают!'}, status=HTTP_400_BAD_REQUEST)
        custom_password_validate(request, password_serializer)
        return Response({'detail': 'Пароль успешно изменен'})
