"""Загрузка JSON-данных консольного приложения."""

from pathlib import Path

from django.conf import settings

from models import Booking, Room, User
from storage import load_bookings, load_rooms, load_users


def load_catalog() -> tuple[list[Room], list[User], list[Booking]]:
    """Прочитать помещения, пользователей и бронирования.

    Returns:
        Три списка объектов предметной области.
    """
    folder = Path(settings.BASE_DIR) / "data"
    rooms = load_rooms(str(folder / "rooms.json"))
    users = load_users(str(folder / "users.json"))
    bookings = load_bookings(
        str(folder / "bookings.json"),
        rooms,
        users,
    )
    return rooms, users, bookings
