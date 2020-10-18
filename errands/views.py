from rest_framework import viewsets, status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import CustomUser
from .serializers import (BoardSerializer, TaskDetailSerializer, TaskListSerializer, BoardBaseSerializer,
                          IconSerializer, TaskUpdateSerializer, BoardFriendSerializer, SoExecutorSerializer)
from .models import Boards, Tasks, Icons, FriendBoardPermission
from .services import add_new_user


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
    serializer_class = TaskListSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if 'icon' in self.request.data:
            try:
                icon = Icons.objects.get(description=self.request.data['icon'])
                serializer.save(icon=icon)
            except Icons.DoesNotExist:
                pass
        if 'first_name' in self.request.data and 'last_name' in self.request.data:
            add_new_user(first_name=self.request.data['first_name'], last_name=self.request.data['last_name'],
                         pk=self.kwargs['pk'], serializer=serializer)
        serializer.save(board_id=self.kwargs['pk'])


class BoardFriendsView(ListAPIView):
    serializer_class = BoardFriendSerializer
    permission_classes = [IsAuthenticated]

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
        task = Tasks.objects.get(id=pk)
        user = CustomUser.objects.get(id=request.data.get('id'))
        task.so_executors.add(user)
        return Response(SoExecutorSerializer(user).data, status=status.HTTP_200_OK)
