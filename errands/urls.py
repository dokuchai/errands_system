from django.urls import path
from .views import BoardRetrieveUpdateView, TaskRetrieveUpdateView, TaskCreateView

urlpatterns = [
    path('board/<int:pk>/', BoardRetrieveUpdateView.as_view()),
    path('task/<int:pk>/', TaskRetrieveUpdateView.as_view()),
    path('board/<int:pk>/create-task/', TaskCreateView.as_view()),
]
