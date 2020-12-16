import debug_toolbar
from django.contrib import admin
from django.urls import path, include

from users.views import CustomUserTokenCreateOrRefresh, RegisterUserView, SendMailResetPasswordView, ProfileUserView, \
    PasswordRefreshView, ResetPasswordView
from .yasg import urlpatterns as swagger_urls

urlpatterns = [
    path('auth/', include('rest_registration.api.urls')),
    path('signin/', CustomUserTokenCreateOrRefresh.as_view()),
    path('register/', RegisterUserView.as_view()),
    path('send-mail-password-reset/', SendMailResetPasswordView.as_view()),
    path('password-refresh/', PasswordRefreshView.as_view()),
    path('password-reset/', ResetPasswordView.as_view()),
    path('admin/', admin.site.urls),
    path('profile/', ProfileUserView.as_view()),
    path('', include('errands.urls')),
    path('__debug__/', include(debug_toolbar.urls)),
]
urlpatterns += swagger_urls
