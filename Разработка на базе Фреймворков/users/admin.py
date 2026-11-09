"""Регистрация пользователей в админке."""

from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Список пользователей предметной области."""

    list_display = ("name", "email")
    search_fields = ("name", "email")
