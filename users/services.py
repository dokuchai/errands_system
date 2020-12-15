from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND

from .authentication import token_expire_handler, expires_in
from .serializers import CustomUserSerializer


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
