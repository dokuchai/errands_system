from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

ACTION_CREATE = 'create'
ACTION_UPDATE = 'update'
ACTION_DELETE = 'delete'


class ChangeLog(models.Model):
    TYPE_ACTION_ON_MODEL = (
        (ACTION_CREATE, _('Создание')),
        (ACTION_UPDATE, _('Изменение')),
        (ACTION_DELETE, _('Удаление')),
    )
    changed = models.DateTimeField(auto_now=True, verbose_name='Дата/время изменения')
    model = models.CharField(max_length=255, verbose_name='Таблица', null=True)
    record_id = models.IntegerField(verbose_name='ID записи', null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='Автор изменения',
        on_delete=models.CASCADE, null=True)
    action_on_model = models.CharField(
        choices=TYPE_ACTION_ON_MODEL, max_length=50, verbose_name='Действие', null=True)
    data = models.JSONField(verbose_name='Изменяемые данные модели', default=dict)
    ipaddress = models.CharField(max_length=15, verbose_name='IP адресс', null=True)

    class Meta:
        ordering = ('changed',)
        verbose_name = _('Лог')
        verbose_name_plural = _('Логи')

    def __str__(self):
        return f'{self.id}'

    @classmethod
    def add(cls, instance, user, ipaddress, action_on_model, data, id=None):
        """Создание записи в журнале регистрации изменений"""
        log = ChangeLog.objects.get(id=id) if id else ChangeLog()
        log.model = instance.__class__.__name__
        log.record_id = instance.pk
        if user:
            log.user = user
        log.ipaddress = ipaddress
        log.action_on_model = action_on_model
        log.data = data
        log.save()
        return log.pk
