import debug_toolbar
from django.contrib import admin
from django.urls import path, include
from users.views import CustomUserTokenCreateOrRefresh, RegisterUserView

urlpatterns = [
    path('signin/', CustomUserTokenCreateOrRefresh.as_view()),
    path('register/', RegisterUserView.as_view()),
    path('admin/', admin.site.urls),
    path('', include('errands.urls')),
    path('__debug__/', include(debug_toolbar.urls)),
]
