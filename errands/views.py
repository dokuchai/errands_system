from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework import viewsets, status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import CustomUser
from .serializers import (BoardSerializer, TaskDetailSerializer, BoardBaseSerializer,
                          IconSerializer, TaskUpdateSerializer, BoardFriendSerializer, SoExecutorSerializer,
                          TaskCreateSerializer, BoardActiveTasksSerializer)
from .models import Boards, Tasks, Icons, FriendBoardPermission
from .services import add_new_user, add_new_responsible


class IconsListView(ListAPIView):
    queryset = Icons.objects.all()
    serializer_class = IconSerializer


class BoardRetrieveUpdateView(viewsets.ModelViewSet):
    queryset = Boards.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BoardBaseSerializer
        elif self.action == "update":
            return BoardSerializer


class BoardTasksActiveView(viewsets.ModelViewSet):
    queryset = Boards.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BoardActiveTasksSerializer
        elif self.action == "update":
            return BoardSerializer


class TaskRetrieveUpdateView(viewsets.ModelViewSet):
    queryset = Tasks.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TaskDetailSerializer
        elif self.action == "partial_update":
            return TaskUpdateSerializer


class TaskCreateView(CreateAPIView):
    queryset = Tasks.objects.all()
    serializer_class = TaskCreateSerializer
    permission_classes = [IsAuthenticated]

    # def post(self, request, *args, **kwargs):
    #     icon, term, project = None, None, ''
    #     if 'icon' in request.data:
    #         try:
    #             icon = Icons.objects.get(description=request.data['icon'])
    #         except Icons.DoesNotExist:
    #             pass
    #     if 'term' in request.data:
    #         term = request.data['term']
    #     if 'project' in request.data:
    #         project = request.data['project']
    #     task = Tasks.objects.create(title=request.data['title'], icon=icon, board_id=self.kwargs['pk'], term=term,
    #                                 project=project)
    #     if 'so_executors' in request.data:
    #         for name in request.data['so_executors']:
    #             name = name.split(' ')
    #             add_new_user(first_name=name[1], last_name=name[0], board_id=self.kwargs['pk'], task=task)
    #     return Response(self.serializer_class(task).data, status=status.HTTP_201_CREATED)
    def perform_create(self, serializer):
        icon, resp = None, None
        executors = []
        if 'icon' in self.request.data:
            try:
                icon = Icons.objects.get(description=self.request.data['icon'])
            except Icons.DoesNotExist:
                pass
        if 'resp_name' in self.request.data:
            name = str(self.request.data['resp_name']).split(' ')
            resp = add_new_responsible(first_name=name[1], last_name=name[0], board_id=self.kwargs['pk'])
        if 'resp_id' in self.request.data:
            resp = CustomUser.objects.get(id=self.request.data['resp_id'])
        if 'exec_name' in self.request.data:
            for executor in self.request.data['exec_name']:
                name = executor.split(' ')
                executors.append(add_new_user(first_name=name[1], last_name=name[0], board_id=self.kwargs['pk']))
        if 'exec_id' in self.request.data:
            for executor in self.request.data['exec_id']:
                executors.append(CustomUser.objects.get(id=executor))
        serializer.save(board_id=self.kwargs['pk'], icon=icon, so_executors=executors, responsible=resp)


class BoardFriendsView(ListAPIView):
    serializer_class = BoardFriendSerializer

    def get_queryset(self):
        friends = FriendBoardPermission.objects.filter(board=self.kwargs["pk"])
        return friends


class FriendView(RetrieveAPIView):
    serializer_class = BoardFriendSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return FriendBoardPermission.objects.get(friend_id=self.kwargs['pk2'], board_id=self.kwargs['pk'])


class AddExecutorView(APIView):
    def post(self, request, pk):
        task, user = Tasks.objects.get(id=pk), None
        if 'id' in request.data:
            try:
                user = CustomUser.objects.get(id=request.data.get('id'))
                task.so_executors.add(user)
            except CustomUser.DoesNotExist:
                return Response({"message": "Пользователь не найден!"}, status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response({"message": "Некорректный тип данных (ожидается целочисленное значение)"},
                                status=status.HTTP_400_BAD_REQUEST)
        elif 'name' in request.data:
            name = str(request.data.get('name')).split(' ')
            user = add_new_user(first_name=name[1], last_name=name[0], board_id=task.board.id)
            task.so_executors.add(user)
        return Response(SoExecutorSerializer(user).data, status=status.HTTP_200_OK)


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
