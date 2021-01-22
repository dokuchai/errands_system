import requests
import xlwt
from django.http import HttpResponse
from django.db.models import Value, F
from django.db.models.functions import Concat
from django.utils.crypto import get_random_string
from rest_framework import exceptions, status
from rest_framework.response import Response

from errands.models import Boards, Tasks, Icons, Project, FriendBoardPermission
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


def hide_request_to_isu(instance):
    url = f"http://isuapi.admlr.lipetsk.ru/api/get-ambulance-messages"
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    content = dict(response.json())
    death_escalation = content['data']['death_escalation']
    ambulances = content['data']['ambulance']
    test_output = content['data']['test_output']
    board = Boards.objects.get(id=instance.id)
    tasks = []
    project_death, project_death_created = Project.objects.get_or_create(title='Смертность')
    project_ambulance, project_ambulance_created = Project.objects.get_or_create(title='Скорая')
    responsible = CustomUser.objects.get(first_name=board.owner.first_name, last_name=board.owner.last_name,
                                         father_name=board.owner.father_name, boards=board)
    responsible_full_name = f"{responsible.last_name} {responsible.first_name} {responsible.father_name}"
    if ambulances:
        get_or_create_isu_tasks(items=ambulances, board=board, responsible_full_name=responsible_full_name,
                                tasks=tasks, project=project_ambulance, responsible=responsible)
    if death_escalation:
        get_or_create_isu_tasks(items=death_escalation, board=board, responsible_full_name=responsible_full_name,
                                tasks=tasks, project=project_death, responsible=responsible)
    if test_output:
        get_or_create_isu_tasks(items=test_output, board=board, responsible_full_name=responsible_full_name,
                                tasks=tasks, project=project_death, responsible=responsible)


def check_request_user_to_relation_with_current_task(task_id, request):
    task = Tasks.objects.get(id=task_id)
    if request.user in task.so_executors.all() or task.responsible == request.user or task.board.owner == request.user \
            or task.board.status == 'Общая':
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


def check_request_user_is_board_owner(self, pk=None):
    if pk is None:
        board = Boards.objects.get(id=self.kwargs['pk'])
        if board.owner != self.request.user:
            raise CustomAPIException({'message': 'Это действие может выполнить только владелец доски'})
    else:
        board = Boards.objects.get(id=pk)
        if board.owner != self.context['user']:
            raise CustomAPIException({'message': 'Это действие может выполнить только владелец доски'})


def reset_user_password(user_id, password, timestamp, signature):
    payload = f'user_id={user_id}&timestamp={timestamp}&signature={signature}&password={password}'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    url = 'https://back-missions.admlr.lipetsk.ru/auth/reset-password/'
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        return Response({'detail': 'Пароль успешно изменен'}).data
    else:
        raise CustomAPIException({'detail': 'Неверные данные'}, status_code=status.HTTP_400_BAD_REQUEST)


def send_mail_password_reset(email):
    url = "https://back-missions.admlr.lipetsk.ru/auth/send-reset-password-link/"
    payload = f'email={email}'
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
        raise CustomAPIException(context, status_code=status.HTTP_404_NOT_FOUND)


def check_user_redactor(self, instance):
    if instance.board.status == 'Общая':
        return True
    try:
        friend = FriendBoardPermission.objects.get(board_id=instance.board.id, friend_id=self.context['user'].id)
        if friend.redactor:
            return True
        else:
            return False
    except FriendBoardPermission.DoesNotExist:
        return False


def increase_version_task(pk):
    task = Tasks.objects.get(id=pk)
    task.version += 1
    task.save()
    return task


def decrease_version_task(pk):
    task = Tasks.objects.get(id=pk)
    task.version -= 1
    task.save()
    return task


def tasks_report(pk):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Task report.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Tasks on 2 selected statuses')

    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Ответственный', 'Задача', 'Статус']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()
    board = Boards.objects.get(id=pk)
    rows = Tasks.objects.filter(board=board, status__in=('Требуется помощь', 'Завершено и подтверждено')).annotate(
        responsible_name=Concat('responsible__first_name', Value(' '), 'responsible__last_name')).values_list(
        'responsible_name', 'title', 'status')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    wb.save(response)
    return response


def output_active_tasks(instance, project_serializer, task_serializer):
    projects = Project.objects.filter(project_tasks__board=instance,
                                      project_tasks__status__in=('В работе', 'Требуется помощь')).distinct()
    tasks = Tasks.objects.filter(board=instance, project=None,
                                 status__in=('В работе', 'Требуется помощь')).order_by(
        F('term').asc(nulls_last=True), 'id')
    return {
        "id": instance.id,
        "title": instance.title,
        "status": instance.status,
        "owner": instance.owner.get_full_name(),
        "projects": project_serializer(projects, many=True, context={'board': instance.id}).data,
        "tasks": task_serializer(tasks, many=True).data
    }


def update_task_logic(instance, validated_data):
    instance.title = validated_data.get('title', instance.title)
    instance.text = validated_data.get('text', instance.text)
    instance.term = validated_data.get('term', instance.term)
    instance.status = validated_data.get('status', instance.status)
    icon, executors = validated_data.pop('icon', None), []
    try:
        instance.icon = Icons.objects.get(description=icon['description'])
    except Icons.DoesNotExist:
        instance.icon = None
    except TypeError:
        pass
    if 'resp_id' in validated_data:
        if str(validated_data['resp_id']).isdigit():
            try:
                instance.responsible = CustomUser.objects.get(id=int(validated_data['resp_id']))
            except CustomUser.DoesNotExist:
                pass
        else:
            instance.responsible = None
    if 'name' in validated_data:
        responsible = None
        name = str(validated_data['name']).split(' ')
        if len(name) == 2:
            try:
                responsible = CustomUser.objects.get(first_name=name[1], last_name=name[0],
                                                     friend_board=instance.board)
            except CustomUser.DoesNotExist:
                responsible = add_new_responsible(first_name=name[1], last_name=name[0],
                                                  board_id=instance.board.id)
        elif len(name) == 1 and name[0] != '':
            try:
                responsible = CustomUser.objects.get(first_name=name[0], last_name='',
                                                     friend_board=instance.board)
            except CustomUser.DoesNotExist:
                responsible = add_new_responsible(first_name=name[0], last_name='',
                                                  board_id=instance.board.id)
        instance.responsible = responsible
    if 'project' in validated_data:
        if validated_data['project'] == 'null' or validated_data['project'] == '':
            instance.project = None
        else:
            project, created = Project.objects.get_or_create(title=validated_data['project'])
            instance.project = project
    if 'exec_name' in validated_data:
        for executor in validated_data['exec_name']:
            name = executor.split(' ')
            if len(name) == 1:
                executors.append(add_new_user(first_name=name[1], last_name='', board_id=instance.board.id))
            elif len(name) == 2:
                executors.append(
                    add_new_user(first_name=name[1], last_name=name[0], board_id=instance.board.id))
    if 'exec_id' in validated_data:
        for executor in validated_data['exec_id']:
            executors.append(CustomUser.objects.get(id=executor))
    instance.so_executors.add(*executors)
    instance.save()


def create_task_logic(data, serializer, board_id):
    icon, resp, project = None, None, None
    executors = []
    if 'icon' in data:
        try:
            icon = Icons.objects.get(description=data['icon'])
        except Icons.DoesNotExist:
            pass
    if 'resp_name' in data and data['resp_name'] != '':
        name = str(data['resp_name']).split(' ')
        if len(name) == 1:
            resp = add_new_responsible(first_name=name[1], last_name='', board_id=board_id)
        elif len(name) == 2:
            resp = add_new_responsible(first_name=name[1], last_name=name[0], board_id=board_id)
    if 'resp_id' in data:
        resp = CustomUser.objects.get(id=data['resp_id'])
    if 'exec_name' in data and data['exec_name']:
        for executor in data['exec_name']:
            name = executor.split(' ')
            if len(name) == 1:
                executors.append(add_new_user(first_name=name[1], last_name='', board_id=board_id))
            elif len(name) == 2:
                executors.append(add_new_user(first_name=name[1], last_name=name[0], board_id=board_id))
    if 'exec_id' in data and data['exec_id']:
        for executor in data['exec_id']:
            executors.append(CustomUser.objects.get(id=executor))
    if 'project' in data:
        if data['project'] != '':
            project, created = Project.objects.get_or_create(title=data['project'])
    serializer.save(board_id=board_id, icon=icon, so_executors=executors, responsible=resp,
                    project=project)
