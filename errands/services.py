from django.utils.crypto import get_random_string

from errands.models import Boards
from users.models import CustomUser


def add_new_user(first_name, last_name, pk, task=None, serializer=None):
    domain = get_random_string(length=5).lower()
    responsible = CustomUser.objects.create(first_name=first_name,
                                            last_name=last_name, email=f'{domain}@new.com')
    board = Boards.objects.get(id=pk)
    board.friends.add(responsible)
    if task:
        task.responsible = responsible
    if serializer:
        serializer.save(responsible=responsible)
