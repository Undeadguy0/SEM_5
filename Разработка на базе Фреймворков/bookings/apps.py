from django.apps import AppConfig


class BookingsConfig(AppConfig):
    """Бронирования Roomly."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "bookings"
    verbose_name = "Бронирования"
