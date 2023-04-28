from django.db import models


class User(models.Model):
    last_name = models.CharField(max_length=20)
    first_name = models.CharField(max_length=20)
    middle_name = models.CharField(max_length=20)
    email = models.CharField(max_length=30)
    login = models.CharField(max_length=30)
    password = models.CharField(max_length=256)
    role = models.IntegerField()
    icon = models.ImageField()


class Project(models.Model):
    title = models.CharField(max_length=20)
    description = models.CharField(max_length=3000)
    manager_id = models.IntegerField()
    leader_id = models.IntegerField()
    date_of_creation = models.DateTimeField()
    status = models.IntegerField()


class Task(models.Model):
    title = models.CharField(max_length=20)
    description = models.CharField(max_length=3000)
    project_id = models.IntegerField()
    executor_id = models.IntegerField()
    lead_id = models.IntegerField()
    reviewer_id = models.IntegerField()
    date_of_creation = models.DateTimeField()
    status = models.IntegerField()
    story_point = models.IntegerField()
    date_of_completion = models.DateTimeField()
    sprint_id = models.IntegerField()


class Comment(models.Model):
    task_id = models.IntegerField()
    author_id = models.IntegerField()
    text = models.CharField(max_length=1000)
    date_of_creation = models.DateTimeField()


class Sprint(models.Model):
    project_id = models.IntegerField()
    date_of_start = models.DateTimeField()
    date_of_end = models.DateTimeField()
