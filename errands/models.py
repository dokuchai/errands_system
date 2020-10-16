from django.db.models.signals import post_delete, post_save
from django.db import models
from users.models import CustomUser

from changelog.mixins import ChangeloggableMixin
from changelog.signals import journal_save_handler, journal_delete_handler


class FriendBoardPermission(ChangeloggableMixin, models.Model):
    board = models.ForeignKey('Boards', on_delete=models.CASCADE)
    friend = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Друг')
    redactor = models.BooleanField('Право на редактирование', default=False)

    class Meta:
        verbose_name = 'Друг доски'
        verbose_name_plural = 'Друзья доски'

    def __str__(self):
        return f'{self.friend.last_name} {self.friend.first_name} {self.friend.father_name}'


post_save.connect(journal_save_handler, sender=FriendBoardPermission)
post_delete.connect(journal_delete_handler, sender=FriendBoardPermission)


class Boards(ChangeloggableMixin, models.Model):
    STATUS = (('Личная', 'Личная'), ('Для друзей', 'Для друзей'), ('Общая', 'Общая'))
    title = models.CharField('Название', max_length=50)
    status = models.CharField('Статус', max_length=10, choices=STATUS, default='Общая')
    history = models.DateTimeField('История', auto_now_add=True)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='boards', verbose_name='Владелец')
    friends = models.ManyToManyField(CustomUser, verbose_name='Друзья доски', related_name='friend_board', blank=True,
                                     through=FriendBoardPermission)

    class Meta:
        verbose_name = 'Доска'
        verbose_name_plural = 'Доски'

    def __str__(self):
        return self.title


post_save.connect(journal_save_handler, sender=Boards)
post_delete.connect(journal_delete_handler, sender=Boards)


class Icons(ChangeloggableMixin, models.Model):
    image = models.ImageField('Иконка', upload_to='icons/')
    description = models.CharField('Описание', max_length=20, default='')

    class Meta:
        verbose_name = 'Иконка'
        verbose_name_plural = 'Иконки'

    def __str__(self):
        return self.description


post_save.connect(journal_save_handler, sender=Icons)
post_delete.connect(journal_delete_handler, sender=Icons)


class Tasks(ChangeloggableMixin, models.Model):
    STATUS = (
        ('В работе', 'В работе'),
        ('Выполнена', 'Выполнена'),
        ('Выполнена и проверена', 'Выполнена и проверена'),
        ('Просрочена', 'Просрочена'),
        ('Отменена', 'Отменена'),
    )
    title = models.CharField('Название', max_length=100)
    text = models.TextField('Текст задачи', blank=True, default='')
    term = models.DateTimeField('Срок', auto_now=False, blank=True, null=True)
    status = models.CharField('Статус', max_length=22, choices=STATUS, default='В работе')
    project = models.CharField('Проект', max_length=100, default='', blank=True)
    board = models.ForeignKey(Boards, on_delete=models.CASCADE, related_name='tasks', verbose_name='Доска', blank=True,
                              null=True)
    responsible = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='responsible',
                                    verbose_name='Ответственный', blank=True, null=True)
    so_executors = models.ManyToManyField(CustomUser, related_name='so_executors', verbose_name='Соисполнители',
                                          blank=True)
    icon = models.ForeignKey(Icons, on_delete=models.PROTECT, related_name='icon', verbose_name='Иконка', blank=True,
                             null=True)
    parent = models.ForeignKey('self', on_delete=models.PROTECT, verbose_name='Родительская задача', blank=True,
                               null=True)

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    def __str__(self):
        return self.title


post_save.connect(journal_save_handler, sender=Tasks)
post_delete.connect(journal_delete_handler, sender=Tasks)
