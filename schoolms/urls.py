"""Pagrindiniai URL maršrutai."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("administracija/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include(("diary.urls", "diary"), namespace="diary")),
]
