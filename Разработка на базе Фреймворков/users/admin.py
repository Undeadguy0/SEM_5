"""Регистрация пользователей в админке."""

from django.contrib import admin

from bookings.models import Booking
from users.models import User


class UserBookingInline(admin.TabularInline):
    """Связанные бронирования на карточке пользователя."""

    model = Booking
    fields = ("room", "booking_date", "status")
    extra = 0
    can_delete = False


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Список пользователей предметной области."""

    list_display = ("id", "name", "email")
    list_display_links = ("name",)
    search_fields = ("name", "email")
    ordering = ("name",)
    list_per_page = 20
    inlines = (UserBookingInline,)
