from django.utils.crypto import get_random_string

from errands.models import Boards, Tasks, Icons
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


def split_task_message(title, message):
    message_dict = {"icon": None, "message": f'{title}. {message}'}
    if str(message).startswith('ИСУ'):
        icon_list = str(message).split(' ')[:2]
        message_list = str(message).split(' ')[2:]
        icon_title = ' '.join(icon_list)
        icon = Icons.objects.get(description__icontains=icon_title)
        split_message = ' '.join(message_list)
        title_with_split_message = f'{title}. {split_message}'
        message_dict.update({"icon": icon.id, "message": title_with_split_message})
    return message_dict


def get_or_create_isu_tasks(items, board, responsible_full_name, tasks, project, responsible):
    recipients_fio_set = set(
        [f'{item["last_name"]} {item["first_name"]} {item["father_name"]}' for item in items])
    if f'{board.owner.last_name} {board.owner.first_name} {board.owner.father_name}' in recipients_fio_set:
        for item in items:
            message_and_icon = split_task_message(title=item['title'], message=item['message'])
            full_name = f"{item['last_name']} {item['first_name']} {item['father_name']}"
            if responsible_full_name == full_name:
                task, created = Tasks.objects.get_or_create(title=message_and_icon['message'], board=board,
                                                            project=project,  responsible=responsible,
                                                            term=item['deadline'], icon_id=message_and_icon['icon'])
                tasks.append(task)
