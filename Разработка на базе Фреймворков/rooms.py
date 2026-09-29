"""Модуль работы с переговорными комнатами."""


def add_room(rooms: dict[int, dict], room_name: str, capacity: int, equipment: list[str]) -> None:
    """Добавить новую переговорную комнату в словарь rooms.

    Args:
        rooms: Словарь переговорных комнат.
        room_name: Название переговорной.
        capacity: Вместимость переговорной.
        equipment: Список оборудования.
    """
    new_id = max(rooms.keys()) + 1 if rooms else 1
    rooms[new_id] = {"name": room_name, "capacity": capacity, "equipment": equipment}


def find_room(rooms: dict[int, dict], query: str) -> list[dict]:
    """Найти переговорные, в названии которых встречается подстрока query.

    Args:
        rooms: Словарь переговорных комнат.
        query: Подстрока для поиска (нечувствительна к регистру).

    Returns:
        Список найденных словарей с данными переговорных.
    """
    query_lower = query.lower()
    return [
        {"id": room_id, **room_data}
        for room_id, room_data in rooms.items()
        if query_lower in room_data["name"].lower()
    ]


def check_room_capacity(rooms: dict[int, dict], room_id: int, min_capacity: int) -> bool:
    """Проверить, вмещает ли комната room_id не менее min_capacity человек.

    Args:
        rooms: Словарь переговорных комнат.
        room_id: ID переговорной.
        min_capacity: Минимально требуемая вместимость.

    Returns:
        True, если вместимость >= min_capacity, иначе False.
    """
    if room_id not in rooms:
        return False
    return rooms[room_id]["capacity"] >= min_capacity


def filter_rooms_by_capacity(rooms: dict[int, dict], min_capacity: int) -> list[dict]:
    """Отобрать переговорные с вместимостью не менее min_capacity.

    Args:
        rooms: Словарь переговорных комнат.
        min_capacity: Минимально требуемая вместимость.

    Returns:
        Список подходящих переговорных с их данными.
    """
    return [
        {"id": room_id, **room_data}
        for room_id, room_data in rooms.items()
        if room_data["capacity"] >= min_capacity
    ]


def filter_rooms_by_equipment(rooms: dict[int, dict], required: list[str]) -> list[dict]:
    """Отобрать переговорные, в которых есть всё оборудование из required.

    Args:
        rooms: Словарь переговорных комнат.
        required: Список требуемого оборудования.

    Returns:
        Список подходящих переговорных с их данными.
    """
    required_lower = [item.lower() for item in required]
    return [
        {"id": room_id, **room_data}
        for room_id, room_data in rooms.items()
        if all(req in [eq.lower() for eq in room_data["equipment"]] for req in required_lower)
    ]


def sort_rooms(rooms: dict[int, dict]) -> list[dict]:
    """Отсортировать переговорные по вместимости (по убыванию).

    Args:
        rooms: Словарь переговорных комнат.

    Returns:
        Отсортированный список переговорных с их данными.
    """
    return sorted(
        [{"id": room_id, **room_data} for room_id, room_data in rooms.items()],
        key=lambda x: x["capacity"],
        reverse=True,
    )
