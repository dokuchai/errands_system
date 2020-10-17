from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    is_staff = models.BooleanField('Статус персонала', default=False)
    is_active = models.BooleanField('Активный', default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    first_name = models.CharField('Имя', max_length=15, blank=True, default='')
    last_name = models.CharField('Фамилия', max_length=30, blank=True, default='')
    father_name = models.CharField('Отчество', max_length=20, blank=True, default='')
    subdivision = models.CharField('Подразделение', max_length=100, blank=True, default='')
    position = models.CharField('Должность', max_length=50, blank=True, default='')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
