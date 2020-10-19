from django.utils.crypto import get_random_string

from errands.models import Boards
from users.models import CustomUser


def add_new_user(first_name, last_name, board_id, task=None, serializer=None):
    domain = get_random_string(length=5).lower()
    user = CustomUser.objects.create(first_name=first_name,
                                     last_name=last_name, email=f'{domain}@new.com')
    board = Boards.objects.get(id=board_id)
    board.friends.add(user)
    if task:
        task.so_executors.add(user)
    if serializer:
        serializer.save(responsible=user)
    return user
