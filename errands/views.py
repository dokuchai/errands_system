from django.utils.crypto import get_random_string
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
    serializer_class = TaskListSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if 'icon' in self.request.data:
            icon = Icons.objects.get(description=self.request.data['icon'])
            serializer.save(icon=icon)
        if 'first_name' in self.request.data and 'last_name' in self.request.data:
            domain = get_random_string(length=5).lower()
            responsible = CustomUser.objects.create(first_name=self.request.data['first_name'],
                                                    last_name=self.request.data['last_name'], email=f'{domain}@new.com')
            board = Boards.objects.get(id=self.kwargs['pk'])
            board.friends.add(responsible)
            serializer.save(responsible=responsible)
        serializer.save(board_id=self.kwargs['pk'])


class BoardFriendsView(ListAPIView):
    serializer_class = BoardFriendSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        friends = FriendBoardPermission.objects.filter(board=self.kwargs["pk"])
        return friends
