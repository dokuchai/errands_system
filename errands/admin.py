from django.contrib import admin
from .models import Boards, Tasks, Icons


class FriendInlineAdmin(admin.TabularInline):
    model = Boards.friends.through
    # readonly_fields = ['redactor']


@admin.register(Boards)
class BoardAdmin(admin.ModelAdmin):
    inlines = (FriendInlineAdmin,)


@admin.register(Tasks)
class TaskAdmin(admin.ModelAdmin):
    pass


@admin.register(Icons)
class IconAdmin(admin.ModelAdmin):
    pass
