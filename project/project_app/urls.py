from django.urls import path
from .views import *

urlpatterns = [
    path("", main_view, name="main_view"),
    path("register/", register, name="register"),
    path("logout/", logout, name="logout")
]
