from django.urls import path
from .views import (BoardRetrieveUpdateView, TaskRetrieveUpdateView, TaskCreateView, IconsListView, BoardFriendsView,
                    FriendView, DeleteExecutorView, BoardTasksActiveView, BoardsListView, ISUView,
                    DeleteFriendToBoardView)

urlpatterns = [
    path('boards/', BoardsListView.as_view()),
    path('board/<int:pk>/', BoardRetrieveUpdateView.as_view({"get": "retrieve", "put": "update"})),
    path('board/<int:pk>/active-tasks/', BoardTasksActiveView.as_view({"get": "retrieve", "put": "update"})),
    path('board/<int:pk>/isu/', ISUView.as_view()),
    path('task/<int:pk>/', TaskRetrieveUpdateView.as_view({"get": "retrieve", "put": "partial_update"})),
    path('task/<int:pk>/delete-executor/', DeleteExecutorView.as_view()),
    path('board/<int:pk>/create-task/', TaskCreateView.as_view()),
    path('board/<int:pk>/friends/', BoardFriendsView.as_view()),
    path('board/<int:pk>/friend/<int:pk2>/', FriendView.as_view()),
    path('board/<int:pk>/delete-friend/', DeleteFriendToBoardView.as_view()),
    path('icons/', IconsListView.as_view()),
]
