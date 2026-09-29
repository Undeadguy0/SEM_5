"""Модуль сохранения и загрузки данных из JSON."""

import json


def load_rooms(filename: str) -> dict[int, dict]:
    """Загрузить переговорные из JSON-файла.

    Args:
        filename: Путь к JSON-файлу.

    Returns:
        Словарь переговорных комнат {id: room_data}.
        При ошибке возвращает пустой словарь.
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            return {}
        rooms: dict[int, dict] = {}
        for item in data:
            room = {key: value for key, value in item.items() if key != "id"}
            rooms[item["id"]] = room
        return rooms
    except (
        FileNotFoundError,
        json.JSONDecodeError,
        TypeError,
        KeyError,
        AttributeError,
    ):
        return {}


def save_rooms(filename: str, rooms: dict[int, dict]) -> None:
    """Сохранить переговорные в JSON-файл.

    Args:
        filename: Путь к JSON-файлу.
        rooms: Словарь переговорных комнат.
    """
    data = [
        {
            "id": room_id,
            **{key: value for key, value in room.items() if key != "id"},
        }
        for room_id, room in rooms.items()
    ]
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_bookings(filename: str) -> list[dict]:
    """Загрузить бронирования из JSON-файла.

    Args:
        filename: Путь к JSON-файлу.

    Returns:
        Список бронирований. При ошибке возвращает пустой список.
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            return []
        return data
    except (FileNotFoundError, json.JSONDecodeError, TypeError):
        return []


def save_bookings(filename: str, bookings: list[dict]) -> None:
    """Сохранить бронирования в JSON-файл.

    Args:
        filename: Путь к JSON-файлу.
        bookings: Список бронирований.
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(bookings, f, ensure_ascii=False, indent=2)
