from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from .authentication import token_expire_handler, expires_in
from .models import CustomUser
from .serializers import CustomUserSerializer
from errands.services import CustomAPIException


def token_stuff(user):
    token, _ = Token.objects.get_or_create(user=user)

    # token_expire_handler will check, if the token is expired it will generate new one
    is_expired, token = token_expire_handler(token)  # The implementation will be described further
    user_serialized = CustomUserSerializer(user)

    return Response({
        'user': user_serialized.data,
        'expires_in': expires_in(token),
        'created': token.created,
        'token': token.key
    }, status=HTTP_200_OK)


def user_partial_update(request, serializer):
    user = CustomUser.objects.get(id=request.user.id)
    if serializer.data['email']:
        if CustomUser.objects.filter(email=serializer.data['email']) and user.email != serializer.data['email']:
            raise CustomAPIException({'message': 'Данный email зарегистрирован на другого пользователя'},
                                     status_code=HTTP_400_BAD_REQUEST)
        user.email = serializer.data['email']
    user.first_name = serializer.data['first_name']
    user.last_name = serializer.data['last_name']
    user.father_name = serializer.data['father_name']
    user.subdivision = serializer.data['subdivision']
    user.position = serializer.data['position']
    password, password_confirm = serializer.data['password'], serializer.data['password_confirm']
    if len(password) > 7 and password == password_confirm:
        user.set_password(password)
        user.save()
        return user
    else:
        raise CustomAPIException({'message': 'Пароль должен состоять из минимум 8 символов'},
                                 status_code=HTTP_400_BAD_REQUEST)
