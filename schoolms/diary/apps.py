"""Aplikacijos konfigūracija."""
from django.apps import AppConfig


class DiaryConfig(AppConfig):
    """Dienyno aplikacijos konfigūracija."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "diary"
    verbose_name = "Dienynas"
