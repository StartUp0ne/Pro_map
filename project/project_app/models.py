from django.db import models
from datetime import datetime


class User(models.Model):
    last_name = models.CharField(max_length=20)
    first_name = models.CharField(max_length=20)
    middle_name = models.CharField(max_length=20)
    email = models.CharField(max_length=30)
    login = models.CharField(max_length=30)
    password = models.CharField(max_length=256)
    role = models.IntegerField(default=3)
    project_id = models.IntegerField(default=0)
    icon = models.ImageField(default="default-user.png")

    def get_role(self):
        role_dict = {1: "manager", 2: "project_leader", 3: "worker"}
        return role_dict[self.role]


class Project(models.Model):
    title = models.CharField(max_length=20)
    description = models.CharField(max_length=3000)
    manager_id = models.IntegerField()
    leader_id = models.IntegerField()
    date_of_creation = models.DateTimeField()
    status = models.CharField(max_length=15)


class Task(models.Model):
    title = models.CharField(max_length=20)
    description = models.CharField(max_length=3000)
    project_id = models.IntegerField()
    executor_id = models.IntegerField()
    lead_id = models.IntegerField()
    reviewer_id = models.IntegerField()
    date_of_creation = models.DateTimeField()
    status = models.CharField(max_length=15)
    story_point = models.IntegerField()
    sprint_id = models.IntegerField()


class Comment(models.Model):
    task_id = models.IntegerField()
    author_id = models.IntegerField()
    text = models.CharField(max_length=1000)
    date_of_creation = models.DateTimeField()

    def __str__(self):
        return self.text


class Sprint(models.Model):
    date_of_start = models.DateTimeField()
    date_of_end = models.DateTimeField()

