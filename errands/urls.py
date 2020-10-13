from django.urls import path
from .views import BoardUpdateView

urlpatterns = [
    path('update-board/<int:pk>/', BoardUpdateView.as_view()),
]
