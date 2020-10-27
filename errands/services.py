from django.utils.crypto import get_random_string

from errands.models import Boards
from users.models import CustomUser


def create_user_and_append_him_to_board_friend(first_name, last_name, board_id):
    domain = get_random_string(length=5).lower()
    user = CustomUser.objects.create(first_name=first_name,
                                     last_name=last_name, email=f'{domain}@new.com')
    board = Boards.objects.get(id=board_id)
    board.friends.add(user)
    return user


def add_new_user(first_name, last_name, board_id, task=None, serializer=None):
    user = create_user_and_append_him_to_board_friend(first_name=first_name, last_name=last_name, board_id=board_id)
    if task:
        task.so_executors.add(user)
    if serializer:
        serializer.save(responsible=user)
    return user


def add_new_responsible(first_name, last_name, board_id):
    user = create_user_and_append_him_to_board_friend(first_name, last_name, board_id)
    return user


def get_month(number):
    months = {"01": "Январь", "02": "Февраль", "03": "Март", "04": "Апрель", "05": "Май", "06": "Июнь", "07": "Июль",
              "08": "Август", "09": "Сентябрь", "10": "Октябрь", "11": "Ноябрь", "12": "Декабрь"}
    return months[number]
