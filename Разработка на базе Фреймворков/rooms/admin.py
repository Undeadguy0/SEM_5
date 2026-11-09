"""Регистрация помещений в админке."""

from django.contrib import admin

from rooms.models import Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    """Список переговорных."""

    list_display = ("name", "capacity")
    search_fields = ("name", "equipment")
