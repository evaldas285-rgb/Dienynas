"""Dienyno maršrutai."""
from django.urls import path

from . import views

app_name = "diary"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("pazymiai/", views.grade_list, name="grade_list"),
    path("pazymiai/naujas/", views.grade_create, name="grade_create"),
    path("namu-darbai/naujas/", views.homework_create, name="homework_create"),
    path("lankomumas/", views.attendance_list, name="attendance_list"),
    path("tvarkarastis/", views.schedule_view, name="schedule"),
]
