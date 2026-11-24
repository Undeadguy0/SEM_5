from django.apps import AppConfig


class RoomsConfig(AppConfig):
    """Помещения Roomly."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "rooms"
    verbose_name = "Помещения"
