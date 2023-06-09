from django.urls import path
from .views import *

urlpatterns = [
    path("", main_view, name="main_view"),
    path("register/", register, name="register"),
    path("logout/", logout, name="logout"),
    path("add_project/", add_project, name="add_project"),
    path("project/<int:project_id>/", project, name="project"),
    path("project/<int:project_id>/edit_project/", edit_project, name="edit_project"),
    path("project/<int:project_id>/delete_project/", delete_project, name="delete_project"),
    path("task/<int:task_id>/", task, name="task"),
    path("project/<int:project_id>/task/<int:task_id>/", task, name="task"),
    path("project/<int:project_id>/add_task/", add_task, name="add_task"),
    path("project/<int:project_id>/task/<int:task_id>/edit_task/", edit_task, name="edit_task"),
    path("project/<int:project_id>/task/<int:task_id>/delete_task/", delete_task, name="delete_task"),
    path("project/<int:project_id>/task/<int:task_id>/close_task/", close_task, name="close_task"),
    path("project/<int:project_id>/task/<int:task_id>/delete_comment/<int:comment_id>/", delete_comment,
         name="delete_comment"),
]
