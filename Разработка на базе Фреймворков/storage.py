"""Сохранение и загрузка данных в JSON."""

import json

from models import Booking, Room, User


def load_rooms(filename: str) -> list[Room]:
    """Загрузить переговорные из JSON-файла.

    Args:
        filename: Путь к файлу.

    Returns:
        Список объектов Room. При ошибке — пустой список.
    """
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, list):
            return []
        rooms: list[Room] = []
        for item in data:
            try:
                rooms.append(Room.from_data(item))
            except (KeyError, TypeError, ValueError):
                continue
        return rooms
    except (FileNotFoundError, json.JSONDecodeError, TypeError):
        return []


def save_rooms(filename: str, rooms: list[Room]) -> None:
    """Сохранить переговорные в JSON-файл.

    Args:
        filename: Путь к файлу.
        rooms: Список объектов Room.
    """
    data = [room.to_dict() for room in rooms]
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def load_users(filename: str) -> list[User]:
    """Загрузить пользователей из JSON-файла.

    Args:
        filename: Путь к файлу.

    Returns:
        Список объектов User. При ошибке — пустой список.
    """
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, list):
            return []
        users: list[User] = []
        for item in data:
            try:
                users.append(User.from_data(item))
            except (KeyError, TypeError, ValueError):
                continue
        return users
    except (FileNotFoundError, json.JSONDecodeError, TypeError):
        return []


def save_users(filename: str, users: list[User]) -> None:
    """Сохранить пользователей в JSON-файл.

    Args:
        filename: Путь к файлу.
        users: Список объектов User.
    """
    data = [user.to_dict() for user in users]
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def _find_room(rooms: list[Room], room_id: int) -> Room | None:
    """Найти комнату по id среди уже загруженных объектов."""
    for room in rooms:
        if room.id == room_id:
            return room
    return None


def _find_user(users: list[User], user_id: int) -> User | None:
    """Найти пользователя по id среди загруженных объектов."""
    for user in users:
        if user.id == user_id:
            return user
    return None


def load_bookings(
    filename: str,
    rooms: list[Room],
    users: list[User],
) -> list[Booking]:
    """Загрузить бронирования и связать их с объектами.

    Если комната или пользователь по id не найдены, запись
    пропускается.

    Args:
        filename: Путь к файлу.
        rooms: Загруженные переговорные.
        users: Загруженные пользователи.

    Returns:
        Список объектов Booking. При ошибке файла — пустой список.
    """
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError, TypeError):
        return []

    if not isinstance(data, list):
        return []

    bookings: list[Booking] = []
    for item in data:
        booking = _booking_from_item(item, rooms, users)
        if booking is not None:
            bookings.append(booking)
    return bookings


def _booking_from_item(
    item: dict,
    rooms: list[Room],
    users: list[User],
) -> Booking | None:
    """Собрать Booking из словаря JSON.

    Args:
        item: Одна запись из файла.
        rooms: Загруженные переговорные.
        users: Загруженные пользователи.

    Returns:
        Объект Booking или None, если связать запись нельзя.
    """
    if not isinstance(item, dict):
        return None
    try:
        room = _find_room(rooms, int(item["room_id"]))
        user = _find_user(users, int(item["user_id"]))
        if room is None or user is None:
            return None
        return Booking(
            booking_id=int(item["id"]),
            room=room,
            user=user,
            booking_date=str(item["booking_date"]),
            start_time=str(item["start_time"]),
            end_time=str(item["end_time"]),
            topic=str(item["topic"]),
            is_cancelled=bool(item.get("is_cancelled", False)),
        )
    except (KeyError, TypeError, ValueError):
        return None


def save_bookings(filename: str, bookings: list[Booking]) -> None:
    """Сохранить бронирования в JSON-файл.

    Args:
        filename: Путь к файлу.
        bookings: Список объектов Booking.
    """
    data = [booking.to_dict() for booking in bookings]
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
