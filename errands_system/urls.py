import debug_toolbar
from django.contrib import admin
from django.urls import path, include

from errands.services import reset_user_password
from users.views import CustomUserTokenCreateOrRefresh, RegisterUserView, ResetPasswordView

urlpatterns = [
    path('signin/', CustomUserTokenCreateOrRefresh.as_view()),
    path('register/', RegisterUserView.as_view()),
    path('password-reset/', ResetPasswordView.as_view()),
    path('reset/<slug:uid>/<slug:token>/', reset_user_password, name='reset'),
    path('admin/', admin.site.urls),
    path('', include('errands.urls')),
    path('__debug__/', include(debug_toolbar.urls)),
]
