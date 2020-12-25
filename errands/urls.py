from django.urls import path
from .views import (BoardRetrieveUpdateView, TaskRetrieveUpdateView, TaskCreateView, IconsListView, BoardFriendsView,
                    FriendView, DeleteExecutorView, BoardTasksActiveView, BoardsListView, ChangeLogsTaskView,
                    AddFriendToBoardView, DeleteFriendToBoardView, ChangeFriendPermissionToBoardView, CheckPointView,
                    CommentsView, FileDelete, ActiveBoardProjects, ClearCheckPointsView, RevisionView)

urlpatterns = [
    path('boards/', BoardsListView.as_view()),
    path('board/<int:pk>/', BoardRetrieveUpdateView.as_view({"get": "retrieve", "put": "update"})),
    path('board/<int:pk>/active-tasks/', BoardTasksActiveView.as_view({"get": "retrieve", "put": "update"})),
    path('board/<int:pk>/create-task/', TaskCreateView.as_view()),
    path('board/<int:pk>/projects/', ActiveBoardProjects.as_view()),
    path('board/<int:pk>/friends/', BoardFriendsView.as_view()),
    path('board/<int:pk>/friend/<int:pk2>/', FriendView.as_view()),
    path('board/<int:pk>/add-friend/', AddFriendToBoardView.as_view()),
    path('board/<int:pk>/friend-permission/', ChangeFriendPermissionToBoardView.as_view()),
    path('board/<int:pk>/delete-friend/', DeleteFriendToBoardView.as_view()),
    path('board/<int:pk>/revision/', RevisionView.as_view()),
    path('task/<int:pk>/', TaskRetrieveUpdateView.as_view({"get": "retrieve", "put": "partial_update"})),
    path('task/<int:pk>/delete-executor/', DeleteExecutorView.as_view()),
    path('task/<int:pk>/changelogs/', ChangeLogsTaskView.as_view()),
    path('task/<int:pk>/checkpoint/', CheckPointView.as_view()),
    path('task/<int:pk>/clear-checkpoints/', ClearCheckPointsView.as_view()),
    path('task/<int:pk>/comment/', CommentsView.as_view()),
    path('task/<int:pk>/delete-file/', FileDelete.as_view()),
    path('icons/', IconsListView.as_view()),
]
