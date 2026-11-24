"""Регистрация помещений в админке."""

from django.contrib import admin

from bookings.models import Booking
from rooms.models import Room


class BookingInline(admin.TabularInline):
    """Связанные бронирования на карточке помещения."""

    model = Booking
    fields = ("user", "booking_date", "status")
    extra = 0
    can_delete = False


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    """Список переговорных."""

    list_display = (
        "id",
        "name",
        "slug",
        "capacity",
        "is_large",
    )
    list_display_links = ("name",)
    list_editable = ("capacity",)
    search_fields = ("name", "equipment")
    list_filter = ("capacity", "is_large")
    ordering = ("name",)
    list_per_page = 20
    readonly_fields = ("slug", "is_large")
    inlines = (BookingInline,)
