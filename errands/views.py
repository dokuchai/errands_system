import requests
from rest_framework import viewsets, status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import CustomUser
from changelog.models import ChangeLog
from changelog.serializers import ChangeLogSerializer
from .serializers import (BoardSerializer, TaskDetailSerializer, BoardBaseSerializer, CommentSerializer,
                          IconSerializer, TaskUpdateSerializer, BoardFriendSerializer, CommentCreateSerializer,
                          TaskCreateSerializer, BoardActiveTasksSerializer, TaskListSerializer, CheckPointSerializer,
                          CheckPointUpdateSerializer, ProjectListSerializer)
from .models import Boards, Tasks, Icons, FriendBoardPermission, Project, CheckPoint, Comment, File
from .services import add_new_user, add_new_responsible, get_or_create_isu_tasks, get_or_create_user, \
    check_request_user_to_relation_with_current_task, check_user_to_relation_with_current_board, \
    check_request_user_is_board_owner


class IconsListView(ListAPIView):
    queryset = Icons.objects.all()
    serializer_class = IconSerializer


class BoardsListView(ListAPIView):
    queryset = Boards.objects.all()
    serializer_class = BoardSerializer


class BoardRetrieveUpdateView(viewsets.ModelViewSet):
    queryset = Boards.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BoardBaseSerializer
        elif self.action == "update":
            return BoardSerializer

    def get_serializer_context(self):
        context = super(BoardRetrieveUpdateView, self).get_serializer_context()
        context.update({'user': self.request.user})
        return context


class BoardTasksActiveView(BoardRetrieveUpdateView):
    def get_serializer_class(self):
        if self.action == "retrieve":
            return BoardActiveTasksSerializer
        elif self.action == "update":
            return BoardSerializer

    def get_serializer_context(self):
        context = super(BoardTasksActiveView, self).get_serializer_context()
        context.update({'user': self.request.user})
        return context


class TaskRetrieveUpdateView(viewsets.ModelViewSet):
    queryset = Tasks.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TaskDetailSerializer
        elif self.action == "partial_update":
            return TaskUpdateSerializer

    def perform_update(self, serializer):
        if 'check_points' in self.request.data and self.request.data['check_points']:
            for checkpoint in self.request.data['check_points']:
                CheckPoint.objects.create(date=checkpoint['date'], text=checkpoint['text'], status=checkpoint['status'],
                                          task_id=self.kwargs['pk'])
        if self.request.FILES:
            for file in self.request.FILES.getlist('files'):
                file_obj = File.objects.create(file=file, task_id=self.kwargs['pk'])
                file_name = str(file_obj).split('/')[-1]
                file_obj.name = file_name
                file_obj.save()
        serializer.save()

    def get_serializer_context(self):
        context = super(TaskRetrieveUpdateView, self).get_serializer_context()
        context.update({'user': self.request.user})
        return context


class TaskCreateView(CreateAPIView):
    queryset = Tasks.objects.all()
    serializer_class = TaskCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        board = Boards.objects.get(id=self.kwargs['pk'])
        if board.status == 'Личная':
            if board.owner == request.user:
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            else:
                return Response({"message": "Пользователь сделал доску приватной, вы не можете создать задачу"},
                                status=status.HTTP_403_FORBIDDEN)
        elif board.status == 'Для друзей':
            if board.owner == request.user or request.user in board.friends.all():
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            else:
                return Response({"message": "Вы не можете добавить задачу, свяжитесь с владельцем доски"},
                                status=status.HTTP_403_FORBIDDEN)
        else:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        icon, resp, project = None, None, None
        executors = []
        if 'icon' in self.request.data:
            try:
                icon = Icons.objects.get(description=self.request.data['icon'])
            except Icons.DoesNotExist:
                pass
        if 'resp_name' in self.request.data and self.request.data['resp_name'] != '':
            name = str(self.request.data['resp_name']).split(' ')
            if len(name) == 1:
                resp = add_new_responsible(first_name=name[1], last_name='', board_id=self.kwargs['pk'])
            elif len(name) == 2:
                resp = add_new_responsible(first_name=name[1], last_name=name[0], board_id=self.kwargs['pk'])
        if 'resp_id' in self.request.data:
            resp = CustomUser.objects.get(id=self.request.data['resp_id'])
        if 'exec_name' in self.request.data and self.request.data['exec_name']:
            for executor in self.request.data['exec_name']:
                name = executor.split(' ')
                if len(name) == 1:
                    executors.append(add_new_user(first_name=name[1], last_name='', board_id=self.kwargs['pk']))
                elif len(name) == 2:
                    executors.append(add_new_user(first_name=name[1], last_name=name[0], board_id=self.kwargs['pk']))
        if 'exec_id' in self.request.data and self.request.data['exec_id']:
            for executor in self.request.data['exec_id']:
                executors.append(CustomUser.objects.get(id=executor))
        if 'project' in self.request.data:
            if self.request.data['project'] != '':
                project, created = Project.objects.get_or_create(title=self.request.data['project'])
        serializer.save(board_id=self.kwargs['pk'], icon=icon, so_executors=executors, responsible=resp,
                        project=project)


class BoardFriendsView(ListAPIView):
    serializer_class = BoardFriendSerializer

    def get_queryset(self):
        check_user_to_relation_with_current_board(self)
        friends = FriendBoardPermission.objects.filter(board=self.kwargs["pk"])
        return friends


class ActiveBoardProjects(ListAPIView):
    serializer_class = ProjectListSerializer

    def get_queryset(self):
        check_user_to_relation_with_current_board(self)
        projects = Project.objects.filter(project_tasks__board_id=self.kwargs['pk']).distinct()
        return projects


class FriendView(RetrieveAPIView):
    serializer_class = BoardFriendSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        check_user_to_relation_with_current_board(self)
        return FriendBoardPermission.objects.get(friend_id=self.kwargs['pk2'], board_id=self.kwargs['pk'])


class DeleteExecutorView(APIView):
    def post(self, request, pk):
        try:
            task, user = Tasks.objects.get(id=pk), CustomUser.objects.get(id=request.data.get('id'))
            if user in task.so_executors.all():
                task.so_executors.remove(user)
                return Response({"message": "Соисполнитель удален!"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Пользователь не является соисполнителем у данной задачи!"},
                                status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({"message": "Пользователя не существует!"}, status=status.HTTP_400_BAD_REQUEST)
        except Tasks.DoesNotExist:
            return Response({"message": "Задачи не существует!"}, status=status.HTTP_400_BAD_REQUEST)


class DeleteFriendToBoardView(APIView):
    def post(self, request, pk):
        check_user_to_relation_with_current_board(self)
        try:
            if FriendBoardPermission.objects.filter(board_id=pk, friend_id=request.data.get('id')).exists():
                FriendBoardPermission.objects.filter(board_id=pk, friend_id=request.data.get('id')).delete()
                return Response({"message": "Друг удален!"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Пользователь не является другом данной доски!"},
                                status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({"message": "Пользователя не существует!"}, status=status.HTTP_400_BAD_REQUEST)
        except Boards.DoesNotExist:
            return Response({"message": "Доски не существует!"}, status=status.HTTP_400_BAD_REQUEST)


class AddFriendToBoardView(APIView):
    def post(self, request, pk):
        check_user_to_relation_with_current_board(self)
        name, user = str(request.data['name']).split(' '), None
        if len(name) == 1:
            user = get_or_create_user(last_name=name[0], first_name='', father_name='')
        elif len(name) == 2:
            user = get_or_create_user(last_name=name[0], first_name=name[1], father_name='')
        elif len(name) == 3:
            user = get_or_create_user(last_name=name[0], first_name=name[1], father_name=name[2])
        friend, created = FriendBoardPermission.objects.get_or_create(board_id=pk, friend_id=user.id)
        return Response(BoardFriendSerializer(friend).data, status=status.HTTP_200_OK)


class ChangeFriendPermissionToBoardView(APIView):
    def post(self, request, pk):
        check_request_user_is_board_owner(self)
        try:
            friend = FriendBoardPermission.objects.get(board_id=pk, friend_id=request.data['id'])
            friend.redactor = request.data['redactor']
            friend.save()
            return Response(BoardFriendSerializer(friend).data, status=status.HTTP_200_OK)
        except Boards.DoesNotExist:
            return Response({"message": "Доски не существует!"}, status=status.HTTP_400_BAD_REQUEST)
        except FriendBoardPermission.DoesNotExist:
            return Response({"message": "Пользователь не является другом доски или его не существует"},
                            status=status.HTTP_400_BAD_REQUEST)


# class ISUView(APIView):
#     def post(self, request, pk):
#         url = f"http://isuapi.admlr.lipetsk.ru/api/get-ambulance-messages"
#         payload = {}
#         headers = {}
#         response = requests.request("GET", url, headers=headers, data=payload)
#         content = dict(response.json())
#         death_escalation = content['data']['death_escalation']
#         ambulances = content['data']['ambulance']
#         test_output = content['data']['test_output']
#         board = Boards.objects.get(id=pk)
#         tasks = []
#         project_death, project_death_created = Project.objects.get_or_create(title='Смертность')
#         project_ambulance, project_ambulance_created = Project.objects.get_or_create(title='Скорая')
#         responsible = CustomUser.objects.get(first_name=board.owner.first_name, last_name=board.owner.last_name,
#                                              father_name=board.owner.father_name, boards=board)
#         responsible_full_name = f"{responsible.last_name} {responsible.first_name} {responsible.father_name}"
#         if ambulances:
#             get_or_create_isu_tasks(items=ambulances, board=board, responsible_full_name=responsible_full_name,
#                                     tasks=tasks, project=project_ambulance, responsible=responsible)
#         if death_escalation:
#             get_or_create_isu_tasks(items=death_escalation, board=board, responsible_full_name=responsible_full_name,
#                                     tasks=tasks, project=project_death, responsible=responsible)
#         if test_output:
#             get_or_create_isu_tasks(items=test_output, board=board, responsible_full_name=responsible_full_name,
#                                     tasks=tasks, project=project_death, responsible=responsible)
#         if tasks:
#             return Response(TaskListSerializer(tasks, many=True).data, status=status.HTTP_201_CREATED)
#         else:
#             return Response({"message": "Задач не найдено!"}, status=status.HTTP_200_OK)


class ChangeLogsTaskView(APIView):
    def get(self, request, pk):
        try:
            task = Tasks.objects.get(id=pk)
            changelogs = ChangeLog.objects.filter(record_id=task.id)
            return Response(ChangeLogSerializer(changelogs, many=True).data, status=status.HTTP_200_OK)
        except Tasks.DoesNotExist:
            return Response({'message': 'Задачи не существует!'}, status=status.HTTP_400_BAD_REQUEST)


class CheckPointView(APIView):
    def post(self, request, pk):
        serializer = CheckPointSerializer(data=request.data)
        if serializer.is_valid():
            checkpoint = CheckPoint.objects.create(date=serializer.data['date'], text=serializer.data['text'],
                                                   task_id=pk)
            return Response(CheckPointSerializer(checkpoint).data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        user_status = check_request_user_to_relation_with_current_task(request=request, task_id=pk)
        if user_status:
            serializer = CheckPointUpdateSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    checkpoint = CheckPoint.objects.get(id=request.data['id'], task_id=pk)
                    if 'date' in request.data:
                        checkpoint.date = serializer.data['date']
                    if 'text' in request.data:
                        checkpoint.text = serializer.data['text']
                    if 'status' in request.data:
                        checkpoint.status = serializer.data['status']
                    checkpoint.save()
                    return Response(CheckPointSerializer(checkpoint).data, status=status.HTTP_200_OK)
                except CheckPoint.DoesNotExist:
                    return Response({'message': 'Чек-поинта не существует!'}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'Вы не можете редактировать чек-лист!'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if CheckPoint.objects.filter(id=request.data.get('id'), task_id=pk).exists():
            CheckPoint.objects.filter(id=request.data.get('id'), task_id=pk).delete()
            return Response({"message": "Чекпоинт удален!"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Чекпоинта не существует!"}, status=status.HTTP_400_BAD_REQUEST)


class CommentsView(APIView):
    def post(self, request, pk):
        user_status = check_request_user_to_relation_with_current_task(request=request, task_id=pk)
        if user_status:
            serializer = CommentCreateSerializer(data=request.data)
            if serializer.is_valid():
                comment = Comment.objects.create(text=serializer.data['text'], task_id=pk, user=request.user)
                return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'Вы не можете добавить комментарий!'}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        user_status = check_request_user_to_relation_with_current_task(request=request, task_id=pk)
        if user_status:
            serializer = CommentCreateSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    comment = Comment.objects.get(id=request.data.get('id'), task_id=pk)
                    if comment.user == request.user:
                        comment.text = serializer.data['text']
                        comment.save()
                        return Response(CommentSerializer(comment).data, status=status.HTTP_200_OK)
                    else:
                        return Response({'message': 'Вы не можете редактировать чужой комментарий!'},
                                        status=status.HTTP_400_BAD_REQUEST)
                except Comment.DoesNotExist:
                    return Response({'message': 'Комментария не существует!'}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'Вы не можете редактировать комментарий!'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user_status = check_request_user_to_relation_with_current_task(task_id=pk, request=request)
        if user_status:
            comment = Comment.objects.filter(id=request.data.get('id'), task_id=pk)
            if comment:
                comment.delete()
                return Response({"message": "Комментарий удален!"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Комментария не существует!"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'Вы не можете удалить комментарий!'}, status=status.HTTP_400_BAD_REQUEST)


class FileDelete(APIView):
    def delete(self, request, pk):
        user_status = check_request_user_to_relation_with_current_task(request=request, task_id=pk)
        if user_status:
            file = File.objects.filter(id=request.data.get('id'), task_id=pk)
            if file:
                file.delete()
                return Response({"message": "Файл удален!"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Файла не существует!"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'У вас недостаточно прав для удаления файла'},
                            status=status.HTTP_400_BAD_REQUEST)

# class RevisionView(APIView):
#     def post(self, request, pk):
#         return Response(TaskListSerializer(get_revision_tasks(request, pk), many=True).data, status=status.HTTP_200_OK)
