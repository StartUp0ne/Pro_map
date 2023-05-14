from datetime import datetime, timedelta
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import User, Project, Task, Comment, Sprint
# from passlib.hash import pbkdf2_sha256
from django.http import HttpResponseRedirect, HttpResponseNotFound


def register(request):
    users = User.objects.all()
    user = User()
    if request.method == "POST":
        user.last_name = request.POST.get("last_name")
        user.first_name = request.POST.get("first_name")
        user.middle_name = request.POST.get("middle_name")
        password = request.POST.get("password")
        # user.password = pbkdf2_sha256(password, rounds=10000, salt_size=20)
        role = request.POST.get("role")
        icon = request.POST.get("icon")
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
        return render(request, "register.html", {"user", user})


def loginform(request):
    if request.method == "POST":
        try:
            user = User.objects.get(username=request.POST['login'])
            if pbkdf2_sha256.vetify(user.password, request.POST['password']):
                request.session['user_id'] = user.id
                return HttpResponseRedirect("/")
        except user.DoesNotExist:
            messages.error(request, "Пользователь с таким логином не найден")
    return render(request, "login.html", None)


def logout(request):
    try:
        del request.session['user_id']
    except KeyError:
        pass
    return HttpResponse("You're logged out.")


def main_view(request):
    try:
        user = request.session["user_id"]
    except Exception:
        return HttpResponseRedirect("")
    current_user = User.objects.get(id=user)
    users = User.objects.all()
    projects = Project.objects.all()
    current_sprint = Sprint.current_sprint()
    tasks = Task.objects.get(sprint_id=current_sprint.id)
    return render(request, "index.html", {"projects": projects,
                                          "tasks": tasks,
                                          "sprint": current_sprint,
                                          "current_user": current_user,
                                          "users": users})


def project(request, project_id: int):
    try:
        user = request.session["user_id"]
    except Exception:
        return HttpResponseRedirect("")
    current_project = Project.objects.get(id=project_id)
    current_user = User.objects.get(id=user)
    sprint = Sprint.current_sprint()
    tasks = Task.objects.get(sprint_id=sprint.id)
    users = User.object.all()
    for user in users:
        if user.id == current_project.leader_id:
            leader = user
    return render(request, "project.html", {"project": current_project,
                                            "current_user": current_user,
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
            new_project.leader_id = request.POST.get('leader_id')
            new_project.date_of_creation = datetime.now()
            new_project.status = request.POST.get('status')
            new_project.save()
            return HttpResponseRedirect('/')
        else:
            return render(request, 'create_project.html', {"project": new_project, "users":  users})
    else:
        HttpResponse()


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
        return HttpResponse("<h2>Недостаточно прав доступа</h2>")


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
            return HttpResponseRedirect("/")
        else:
            return render(request, "edit_project.html", {"user": user, "project": current_project})
    else:
        return HttpResponse("<h2>Недостаточно прав доступа</h2>")


def task(request, task_id: int):
    try:
        user = request.session['user_id']
    except Exception:
        user = None
        return HttpResponseRedirect('')
    current_user = User.objects.get(id=user)
    users = User.objects.all()
    current_task = Task.objects.get(task=task_id)
    comments = Comment.objects.get(task_id=task_id)
    if request.method == "POST":
        new_comment = Comment()
        new_comment.text = request.POST.get('new_comment')
        new_comment.date_of_creation = datetime.now()
        new_comment.author_id = current_user.id
        new_comment.task_id = current_task.id
        new_comment.save()
    return render(request, "task.html", {"tasks": current_task,
                                         "users": users,
                                         "user": current_user,
                                         "comments": comments})


def add_task(request, project_id: int):
    try:
        user = request.session['user_id']
    except Exception:
        user = None
        return HttpResponseRedirect('')
    user = User.objects.get(id=user)
    current_project = Project.objects.get(id=project_id)
    new_task = Task()
    if user.get_role() == "manager" or user.get_role() == "project_leader":
        if request.method == "POST":
            new_task.title = request.POST.get('title')
            new_task.description = request.POST.get('description')
            new_task.project_id = project_id
            new_task.lead_id = current_project.leader_id
            new_task.reviewer_id = request.POST.get('reviewer_id')
            new_task.date_of_creation = datetime.now()
            new_task.status = request.POST.get('status')
            new_task.story_point = request.POST.get('story_point')
            new_task.end_date = new_task.date_of_creation + timedelta(days=new_task.story_point)
            new_task.sprint_id = request.POST.get('sprint')
            new_task.save()
            return HttpResponseRedirect("/")
        else:
            return render(request, "add_task.html", {"user": user, "project": current_project, "task": new_task})
    else:
        return HttpResponse("<h2>Недостаточно прав доступа</h2>")


def edit_task(request, task_id: int):
    try:
        user = request.session['user_id']
    except Exception:
        user = None
        return HttpResponseRedirect('')
    try:
        current_task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return HttpResponseNotFound("<h2>This task not found</h2>")
    user = User.objects.get(id=user)
    if user.get_role() == "manager" or user.get_role() == "project_leader":
        if request.method == "POST":
            current_task.title = request.POST.get('title')
            current_task.description = request.POST.get('description')
            current_task.reviewer_id = request.POST.get('reviewer_id')
            current_task.status = request.POST.get('status')
            current_task.story_point = request.POST.get('story_point')
            current_task.end_date = current_task.date_of_creation + timedelta(days=current_task.story_point)
            current_task.sprint_id = request.POST.get('sprint')
            current_task.save()
            return HttpResponseRedirect("/")
        else:
            return render(request, "add_task.html", {"user": user, "task": current_task})
    elif user.get_role() == "worker":
        if request.method == "POST":
            current_task.reviewer_id = request.POST.get('reviewer_id')
            current_task.status = request.POST.get('status')
            current_task.story_point = request.POST.get('story_point')
            current_task.end_date = current_task.date_of_creation + timedelta(days=current_task.story_point)
            current_task.save()
            return HttpResponseRedirect("/")
        else:
            return render(request, "add_task.html", {"user": user, "task": current_task})
    else:
        return HttpResponse("<h2>Недостаточно прав доступа</h2>")


def delete_task(request, task_id: int):
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
            return HttpResponseRedirect("/")
        except Task.DoesNotExist:
            return HttpResponseNotFound("<h2>This task not found</h2>")
    else:
        return HttpResponseNotFound("<h2>Недостаточно прав доступа</h2>")


def add_comment(request, task_id: int):
    try:
        user = request.session['user_id']
    except Exception:
        user = None
        return HttpResponseRedirect("")
    new_comment = Comment()
    try:
        current_task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return HttpResponseNotFound("<h2>Task not found</h2>")
    sprint = Sprint.current_sprint()
    if request.method == "POST":
        new_comment.task_id = task_id
        new_comment.author_id = user.id
        new_comment.text = request.POST.get('text')
        new_comment.date_of_creation = datetime.now()
        new_comment.save()
        return HttpResponseRedirect("/")
    else:
        return render(request, 'task.html', {"tasks": current_task,
                                             "sprint": sprint,
                                             "user": user,
                                             "comments": new_comment})


def edit_comment(request, comment_id: int):
    try:
        user = request.session['user_id']
    except Exception:
        user = None
        return HttpResponseRedirect("")
    try:
        current_comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return HttpResponseRedirect("/")
    current_task = Task.objects.get(id=current_comment.task_id)
    sprint = Sprint.objects.get(id=current_task.sprint_id)
    if request.method == "POST":
        current_comment.text = request.POST.get('text')
        current_comment.save()
        return HttpResponseRedirect("/")
    else:
        return render(request, 'task.html', {"tasks": current_task,
                                             "sprint": sprint,
                                             "user": user,
                                             "comments": current_task})


def delete_comment(request, comment_id: int):
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
        return HttpResponseRedirect("/")
    else:
        return HttpResponseNotFound("<h2>Недостаточно прав доступа</h2>")


def declare_new_sprint(request):
    try:
        user = request.session['user_id']
    except Exception:
        user = None
        return HttpResponseRedirect("")
    user = User.objects.get(id=user)
    new_sprint = Sprint()
    if user.get_role() == "manager" or user.get_role() == "project_leader":
        if request.method == "POST":
            new_sprint.date_of_start = request.POST.get('start')
            new_sprint.date_of_end = request.POST.get('end')
            new_sprint.save()
            return HttpResponseRedirect('')
        else:
            return render(request, 'declare_sprint.html', {"user": user,
                                                           "sprint": new_sprint})
