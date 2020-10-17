from django.contrib.auth import authenticate
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CustomUser
from .serializers import CustomUserSerializer, UserSignInSerializer, NewUserSerializer
from .authentication import token_expire_handler, expires_in


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

        # TOKEN STUFF
        token, _ = Token.objects.get_or_create(user=user)

        # token_expire_handler will check, if the token is expired it will generate new one
        is_expired, token = token_expire_handler(token)  # The implementation will be described further
        user_serialized = CustomUserSerializer(user)

        return Response({
            'user': user_serialized.data,
            'expires_in': expires_in(token),
            'token': token.key
        }, status=HTTP_200_OK)


class NewUserView(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = NewUserSerializer


@receiver(post_save, sender=CustomUser)
def create_random_email(instance, created, **kwargs):
    user = instance
    domain = get_random_string(length=5).lower()
    if created:
        user.email = f'{domain}@new.com'
        user.save()
