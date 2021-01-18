from django.contrib import admin
from .models import Boards, Tasks, Icons, Project, Comment, File


class FriendInlineAdmin(admin.TabularInline):
    model = Boards.friends.through
    # readonly_fields = ['redactor']
    extra = 1


class FilesInLineAdmin(admin.TabularInline):
    model = File
    extra = 1


class CommentsInLineAdmin(admin.TabularInline):
    model = Comment
    readonly_fields = ['parent']
    extra = 1


@admin.register(Boards)
class BoardAdmin(admin.ModelAdmin):
    inlines = (FriendInlineAdmin,)


@admin.register(Tasks)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'board')
    readonly_fields = ['parent']
    inlines = [FilesInLineAdmin, CommentsInLineAdmin]


@admin.register(Icons)
class IconAdmin(admin.ModelAdmin):
    pass


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass


@admin.register(Comment)
class CommentsAdmin(admin.ModelAdmin):
    readonly_fields = ['parent']


@admin.register(File)
class FilesAdmin(admin.ModelAdmin):
    pass
