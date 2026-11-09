"""Регистрация бронирований в админке."""

from django.contrib import admin

from bookings.models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Список бронирований со связями."""

    list_display = (
        "booking_date",
        "room",
        "user",
        "is_cancelled",
    )
    list_filter = ("is_cancelled", "booking_date")
    search_fields = ("topic", "room__name", "user__name")
