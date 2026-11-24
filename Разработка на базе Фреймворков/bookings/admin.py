"""Регистрация бронирований в админке."""

from django.contrib import admin

from bookings.models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Список бронирований со связями."""

    list_display = (
        "id",
        "room",
        "user",
        "booking_date",
        "status",
    )
    list_display_links = ("id",)
    search_fields = ("topic", "room__name", "user__name")
    list_filter = ("status", "booking_date")
    ordering = ("-booking_date",)
    list_per_page = 20
