from django.contrib import admin
from .models import User, Project, Task, Sprint, Comment

admin.site.register(User)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Sprint)
admin.site.register(Comment)
