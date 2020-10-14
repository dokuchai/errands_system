from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated

from .serializers import BoardSerializer, TaskDetailSerializer, TaskListSerializer
from .models import Boards, Tasks


class BoardRetrieveUpdateView(RetrieveUpdateAPIView):
    queryset = Boards.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]


class TaskRetrieveUpdateView(RetrieveUpdateAPIView):
    queryset = Tasks.objects.all()
    serializer_class = TaskDetailSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class TaskCreateView(CreateAPIView):
    queryset = Tasks.objects.all()
    serializer_class = TaskListSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(board_id=self.kwargs['pk'])
