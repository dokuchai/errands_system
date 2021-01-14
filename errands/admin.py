from django.contrib import admin
from .models import Boards, Tasks, Icons, Project, Comment, File


class FriendInlineAdmin(admin.TabularInline):
    model = Boards.friends.through
    # readonly_fields = ['redactor']


@admin.register(Boards)
class BoardAdmin(admin.ModelAdmin):
    inlines = (FriendInlineAdmin,)


@admin.register(Tasks)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'board')
    # readonly_fields = ['version']


@admin.register(Icons)
class IconAdmin(admin.ModelAdmin):
    pass


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass


@admin.register(Comment)
class CommentsAdmin(admin.ModelAdmin):
    pass


@admin.register(File)
class FilesAdmin(admin.ModelAdmin):
    pass
