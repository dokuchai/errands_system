import requests
from django.utils.crypto import get_random_string
from rest_framework import exceptions, status
from rest_framework.response import Response

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


def check_user_to_relation_with_current_board(self):
    board = Boards.objects.get(id=self.kwargs['pk'])
    if board.status == 'Личная' and board.owner != self.request.user:
        raise CustomAPIException(
            {'message': 'Владелец доски сделал ее приватной, Вы не можете взаимодействовать с ней'})
    elif board.status == 'Для друзей' and self.request.user not in board.friends.all() and \
            self.request.user != board.owner:
        raise CustomAPIException({'message': 'Вы не являетесь участником доски'})


def check_user_to_relation_with_current_board_in_serializer(self, instance):
    if instance.status == 'Личная' and instance.owner != self.context['user']:
        raise CustomAPIException(
            {'message': 'Это личная доска другого пользователя, Вы не можете посмотреть содержимое'})
    elif instance.status == 'Для друзей' and self.context['user'] != instance.owner and self.context['user'] not \
            in instance.friends.all():
        raise CustomAPIException(
            {'message': 'Вы не являетесь участником доски и не можете просмотреть содержимое!'})


def check_request_user_is_board_owner(self):
    board = Boards.objects.get(id=self.kwargs['pk'])
    if board.owner != self.request.user:
        raise CustomAPIException({'message': 'Это действие может выполнить только владелец доски'})


def reset_user_password(user_id, password, timestamp, signature):
    payload = f'user_id={user_id}&timestamp={timestamp}&signature={signature}&password={password}'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    # url = 'http://localhost:8000/auth/reset-password/'
    url = 'https://back-missions.admlr.lipetsk.ru/auth/reset_password/'
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        return Response({'detail': 'Пароль успешно изменен'}).data
    else:
        return Response({'detail': 'Неверные данные'}).data


def send_mail_password_reset(email):
    # url = "http://localhost:8000/auth/send-reset-password-link/"
    url = "https://back-missions.admlr.lipetsk.ru/auth/send-reset-password-link/"
    payload = f'login={email}'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        context = {'success': True,
                   'detail': 'Успешно. На Ваш почтовый ящик направлено письмо со ссылкой на сброс пароля'}
        return Response(context).data
    elif response.status_code == 404:
        context = {'success': False, 'detail': 'Пользователь с таким Email не найден'}
        return Response(context).data
