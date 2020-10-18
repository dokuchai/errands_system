from rest_framework import viewsets
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated

from users.models import CustomUser
from .serializers import (BoardSerializer, TaskDetailSerializer, TaskListSerializer, BoardBaseSerializer,
                          IconSerializer, TaskUpdateSerializer, BoardFriendSerializer)
from .models import Boards, Tasks, Icons, FriendBoardPermission


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
    serializer_class = TaskUpdateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(board_id=self.kwargs['pk'])


class BoardFriendsView(ListAPIView):
    serializer_class = BoardFriendSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        friends = FriendBoardPermission.objects.filter(board=self.kwargs["pk"])
        return friends
