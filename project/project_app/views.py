import logging
from datetime import datetime, timedelta, timezone

import dateutil.parser
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import User, Project, Task, Comment, Sprint
from hashlib import pbkdf2_hmac
from django.http import HttpResponseRedirect, HttpResponseNotFound


def register(request):
    users = User.objects.all()
    user = User()
    if request.method == "POST":
        user.last_name = request.POST.get("last_name")
        user.first_name = request.POST.get("first_name")
        user.middle_name = request.POST.get("middle_name")
        password = request.POST.get("password")
        user.password = str(pbkdf2_hmac(hash_name="sha256",
                                        password=password.encode('utf-8'),
                                        salt=b'bad salt'*2,
                                        iterations=10000))
        email = request.POST.get("email")
        login = request.POST.get("login")
        for u in users:
            if login == u.login:
                messages.error(request, "Пользователь с таким логином уже существует")
                return render(request, "register.html", {"user": user})
            elif email == u.email:
                messages.error(request, "Пользователь с такой электронной почтой уже существует")
                return render(request, "register.html", {"user": user})
        user.email = request.POST.get("email")
        user.login = request.POST.get("login")
        user.save()
        return HttpResponseRedirect("/")
    else:
        return render(request, "register.html", None)


def logout(request):
    try:
        del request.session['user_id']
    except KeyError:
        pass
    return HttpResponseRedirect("/")


def main_view(request):
    try:
        user = request.session["user_id"]
    except Exception:
        if request.method == "POST":
            try:
                user = User.objects.get(login=request.POST['login'])
                password = str(pbkdf2_hmac(hash_name="sha256",
                                           password=request.POST['password'].encode('utf-8'),
                                           salt=b'bad salt'*2,
                                           iterations=10000))
                if user.password == password:
                    request.session['user_id'] = user.id
                    return HttpResponseRedirect("/")
                else:
                    messages.error(request, "Неверный пароль")
            except User.DoesNotExist:
                messages.error(request, "Пользователь с таким логином не найден")
        return render(request, "index.html", None)

    current_user = User.objects.get(id=user)
    users = User.objects.all()
    projects = Project.objects.all()
    sprints = Sprint.objects.all()
    current_sprint = None
    for sprint in sprints:
        if sprint.date_of_start <= datetime.now(timezone.utc) <= sprint.date_of_end:
            current_sprint = sprint
    tasks = Task.objects.all()

    if current_user.get_role() == "manager":
        if request.method == "POST":
            sprint = Sprint()
            sprint.date_of_start = dateutil.parser.parse(request.GET.get("start"), ignoretz=True, fuzzy=True)
            days = int(request.GET.get("days"))
            sprint.date_of_end = sprint.date_of_start + timedelta(days=days)
            sprint.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    return render(request, "index.html", {"projects": projects,
                                          "tasks": tasks,
                                          "sprint": current_sprint,
                                          "current_user": current_user,
                                          "users": users})


def project(request, project_id: int):
    try:
        user = request.session["user_id"]
    except Exception:
        return HttpResponseRedirect("/")
    current_project = Project.objects.get(id=project_id)
    current_user = User.objects.get(id=user)
    tasks = Task.objects.all()
    users = User.objects.all()
    leader = User.objects.get(id=current_project.leader_id)
    return render(request, "project.html", {"project": current_project,
                                            "current_user": current_user,
                                            "users": users,
                                            "tasks": tasks,
                                            "leader": leader})


def add_project(request):
    try:
        user = request.session["user_id"]
    except Exception:
        return HttpResponseRedirect("")
    user = User.objects.get(id=user)
    new_project = Project()
    users = User.objects.all()
    if user.get_role() == "manager":
        if request.method == "POST":
            new_project.title = request.POST.get('title')
            new_project.description = request.POST.get('description')
            new_project.manager_id = user.id
            try:
                leader = User.objects.get(id=request.POST.get('leader_id'))

                leader.role = 2
                leader.save()
            except Exception:
                return render(request, 'create_project.html', None)
            new_project.leader_id = leader.id
            new_project.date_of_creation = datetime.now()
            new_project.status = request.POST.get('status')
            logging.error(f"Статус: {new_project.status}")
            new_project.save()
            return HttpResponseRedirect("/")
        else:
            return render(request, 'create_project.html', {"project": new_project, "users":  users})
    else:
        return HttpResponseNotFound("<h2> Не достаточно прав доступа <h2>")


def delete_project(request, project_id: int):
    try:
        user = request.session['user_id']
    except Exception:
        user = None
        return HttpResponseRedirect("")
    user = User.objects.get(id=user)
    if user.get_role() == 'manager':
        try:
            current_project = Project.objects.get(id=project_id)
            current_project.delete()
            return HttpResponseRedirect("/")
        except Project.DoesNotFound:
            return HttpResponseNotFound("<h2>Project not found</h2>")
    else:
        return HttpResponseNotFound("<h2>Недостаточно прав доступа</h2>")


def edit_project(request, project_id: int):
    try:
        user = request.session['user_id']
    except Exception:
        user = None
        return HttpResponseRedirect('')
    user = User.objects.get(id=user)
    try:
        current_project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return HttpResponseNotFound("<h2>Project not found</h2>")

    if user.id == current_project.manager_id or user.id == current_project.leader_id:
        if request.method == "POST":
            current_project.title = request.POST.get('title')
            current_project.description = request.POST.get('description')
            current_project.status = request.POST.get('status')
            current_project.leader_id = request.POST.get('leader_id')
            current_project.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        else:
            return render(request, "edit_project.html", {"user": user,
                                                         "project": current_project})
    else:
        return HttpResponseNotFound("<h2>Недостаточно прав доступа</h2>")


def task(request, project_id: int, task_id: int):
    try:
        user = request.session['user_id']
    except Exception:
        user = None
        return HttpResponseRedirect('')
    current_user = User.objects.get(id=user)
    users = User.objects.all()
    current_task = Task.objects.get(id=task_id)
    comments = Comment.objects.all()

    if request.method == "POST":
        new_comment = Comment()
        new_comment.text = request.POST.get('new_comment')
        new_comment.date_of_creation = datetime.now()
        new_comment.author_id = current_user.id
        new_comment.task_id = current_task.id
        new_comment.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return render(request, "task.html", {"task": current_task,
                                         "users": users,
                                         "user": current_user,
                                         "comments": comments})


def add_task(request, project_id: int):
    try:
        user = request.session['user_id']
    except Exception:
        user = None
        return HttpResponseRedirect('')

    current_user = User.objects.get(id=user)
    users = User.objects.all()
    current_project = Project.objects.get(id=project_id)
    sprints = Sprint.objects.all()
    current_sprint = None
    for sprint in sprints:
        if sprint.date_of_start <= datetime.now(timezone.utc) <= sprint.date_of_end:
            current_sprint = sprint
    new_task = Task()
    if current_user.get_role() == "manager" or current_user.get_role() == "project_leader":
        if request.method == "POST":
            new_task.title = request.POST.get('title')
            new_task.description = request.POST.get('description')
            new_task.project_id = project_id
            new_task.lead_id = current_project.leader_id
            new_task.executor_id = request.POST.get('executor')
            new_task.reviewer_id = request.POST.get('reviewer')
            new_task.date_of_creation = datetime.now()
            new_task.status = request.POST.get('status')
            new_task.story_point = request.POST.get('story_point')
            new_task.sprint_id = request.POST.get('sprint')
            new_task.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        return render(request, "create_task.html", {"current_user": current_user,
                                                    "project": current_project,
                                                    "sprints": sprints,
                                                    "users": users,
                                                    "task": new_task})
    else:
        return HttpResponseNotFound("<h2>Недостаточно прав доступа</h2>")


def edit_task(request, project_id: int, task_id: int):
    try:
        user = request.session['user_id']
    except Exception:
        user = None
        return HttpResponseRedirect('')
    try:
        current_task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return HttpResponseNotFound("<h2>This task not found</h2>")
    users = User.objects.all()
    current_user = User.objects.get(id=user)
    if current_user.get_role() == "manager" or current_user.get_role() == "project_leader":
        if request.method == "POST":
            current_task.title = request.POST.get('title')
            current_task.description = request.POST.get('description')
            current_task.reviewer_id = request.POST.get('reviewer')
            current_task.executor_id = request.POST.get('executor')
            current_task.status = request.POST.get('status')
            current_task.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        else:
            return render(request, "edit_task.html", {"current_user": current_user,
                                                      "users": users,
                                                      "task": current_task})
    elif user.get_role() == "worker":
        if request.method == "POST":
            current_task.reviewer_id = request.POST.get('reviewer_id')
            current_task.status = request.POST.get('status')
            current_task.story_point = request.POST.get('story_point')
            current_task.save()
            return HttpResponseRedirect("/")
        else:
            return render(request, "edit_task.html", {"user": current_user,
                                                      "users": users,
                                                      "task": current_task})
    else:
        return HttpResponseNotFound("<h2>Недостаточно прав доступа</h2>")


def delete_task(request, project_id: int, task_id: int):
    try:
        user = request.session['user_id']
    except Exception:
        user = None
        return HttpResponseRedirect("")
    user = User.objects.get(id=user)
    if user.get_role() == "manager" or user.get_role() == "project_leader":
        try:
            current_task = Task.objects.get(id=task_id)
            current_task.delete()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        except Task.DoesNotExist:
            return HttpResponseNotFound("<h2>This task not found</h2>")
    else:
        return HttpResponseNotFound("<h2>Недостаточно прав доступа</h2>")


def delete_comment(request, project_id: int, task_id: int, comment_id: int):
    try:
        user = request.session['user_id']
    except Exception:
        user = None
        return HttpResponseRedirect("")
    try:
        current_comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return HttpResponseNotFound("<h2>Comment not found</h2>")
    user = User.objects.get(id=user)
    if user.get_role() == "manager" or user.get_role() == "project_leader" or user.id == current_comment.author_id:
        current_comment.delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    else:
        return HttpResponseNotFound("<h2>Недостаточно прав доступа</h2>")

