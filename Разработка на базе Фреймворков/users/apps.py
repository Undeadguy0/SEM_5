"""Конфигурация приложения пользователей."""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Пользователи предметной области Roomly."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "users"
    verbose_name = "Пользователи"
