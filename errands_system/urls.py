from django.contrib import admin
from django.urls import path, include
from users.views import CustomUserTokenCreateOrRefresh

urlpatterns = [
    path('signin/', CustomUserTokenCreateOrRefresh.as_view()),
    path('admin/', admin.site.urls),
    path('', include('errands.urls')),
]
