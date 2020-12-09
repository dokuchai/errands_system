from django.utils.crypto import get_random_string
from rest_framework import exceptions, status

from errands.models import Boards, Tasks, Icons
from users.models import CustomUser


def create_user_and_append_him_to_board_friend(first_name, last_name, board_id):
    domain = get_random_string(length=5).lower()
    user = CustomUser.objects.create(first_name=first_name,
                                     last_name=last_name, email=f'{domain}@new.com')
    board = Boards.objects.get(id=board_id)
    board.friends.add(user)
    return user


def get_or_create_user(first_name, last_name, father_name):
    domain = get_random_string(length=5).lower()
    try:
        user = CustomUser.objects.get(first_name=first_name, last_name=last_name, father_name=father_name)
    except CustomUser.DoesNotExist:
        user = CustomUser.objects.create(first_name=first_name, last_name=last_name, father_name=father_name,
                                         email=f'{domain}@new.com')
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


def split_task_message(message):
    message_dict = {"icon": None, "message": message}
    if str(message).startswith('ИСУ'):
        icon_list = str(message).split(' ')[:2]
        message_list = str(message).split(' ')[2:]
        icon_title = ' '.join(icon_list)
        icon = Icons.objects.get(description__icontains=icon_title)
        split_message = ' '.join(message_list)
        message_dict.update({"icon": icon.id, "message": split_message})
    return message_dict


def get_or_create_isu_tasks(items, board, responsible_full_name, tasks, project, responsible):
    recipients_fio_set = set(
        [f'{item["last_name"]} {item["first_name"]} {item["father_name"]}' for item in items])
    if f'{board.owner.last_name} {board.owner.first_name} {board.owner.father_name}' in recipients_fio_set:
        for item in items:
            message_and_icon = split_task_message(message=item['message'])
            full_name = f"{item['last_name']} {item['first_name']} {item['father_name']}"
            if responsible_full_name == full_name:
                task, created = Tasks.objects.get_or_create(title=message_and_icon['message'], board=board,
                                                            project=project, responsible=responsible,
                                                            term=item['deadline'], icon_id=message_and_icon['icon'])
                if created:
                    tasks.append(task)


def check_request_user_to_relation_with_current_task(task_id, request):
    task = Tasks.objects.get(id=task_id)
    if request.user in task.so_executors.all() or task.responsible == request.user or task.board.owner == request.user:
        return True
    else:
        return False


class CustomAPIException(exceptions.APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = 'error'

    def __init__(self, detail, status_code=None):
        self.detail = detail
        if status_code is not None:
            self.status_code = status_code
