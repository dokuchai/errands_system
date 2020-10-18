from django.urls import path
from .views import BoardRetrieveUpdateView, TaskRetrieveUpdateView, TaskCreateView, IconsListView

urlpatterns = [
    path('board/<int:pk>/', BoardRetrieveUpdateView.as_view({"get": "retrieve", "put": "update"})),
    path('task/<int:pk>/', TaskRetrieveUpdateView.as_view({"get": "retrieve", "put": "partial_update"})),
    path('board/<int:pk>/create-task/', TaskCreateView.as_view()),
    path('icons/', IconsListView.as_view()),
]
