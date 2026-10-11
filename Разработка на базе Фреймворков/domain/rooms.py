"""Функции работы с переговорными комнатами."""

from models import Room


def add_room(
    rooms: list[Room],
    room_name: str,
    capacity: int,
    equipment: list[str],
) -> Room:
    """Добавить новую переговорную в список rooms.

    Args:
        rooms: Список переговорных.
        room_name: Название.
        capacity: Вместимость.
        equipment: Список оборудования.

    Returns:
        Созданный объект Room.
    """
    new_id = max((room.id for room in rooms), default=0) + 1
    room = Room(new_id, room_name, capacity, equipment)
    rooms.append(room)
    return room


def get_room_by_id(rooms: list[Room], room_id: int) -> Room | None:
    """Найти переговорную по идентификатору.

    Args:
        rooms: Список переговорных.
        room_id: Идентификатор комнаты.

    Returns:
        Объект Room или None, если комната не найдена.
    """
    for room in rooms:
        if room.id == room_id:
            return room
    return None


def find_room_by_id(rooms: list[Room], room_id: int) -> Room | None:
    """Найти помещение по идентификатору.

    Args:
        rooms: Список помещений.
        room_id: Идентификатор комнаты.

    Returns:
        Объект Room или None, если комната не найдена.
    """
    return get_room_by_id(rooms, room_id)


def find_room(rooms: list[Room], query: str) -> list[Room]:
    """Найти переговорные по подстроке названия.

    Args:
        rooms: Список переговорных.
        query: Подстрока поиска, без учёта регистра.

    Returns:
        Список подходящих комнат.
    """
    query_lower = query.lower()
    return [room for room in rooms if query_lower in room.name.lower()]


def check_room_capacity(
    rooms: list[Room],
    room_id: int,
    min_capacity: int,
) -> bool:
    """Проверить вместимость комнаты room_id.

    Args:
        rooms: Список переговорных.
        room_id: Идентификатор комнаты.
        min_capacity: Минимальное число мест.

    Returns:
        True, если комната есть и подходит по вместимости.
    """
    room = get_room_by_id(rooms, room_id)
    if room is None:
        return False
    return room.is_suitable_for(min_capacity)


def filter_rooms_by_capacity(
    rooms: list[Room],
    min_capacity: int,
) -> list[Room]:
    """Отобрать переговорные с вместимостью не меньше min_capacity.

    Args:
        rooms: Список переговорных.
        min_capacity: Минимальное число мест.

    Returns:
        Список подходящих комнат.
    """
    return [room for room in rooms if room.is_suitable_for(min_capacity)]


def filter_rooms_by_equipment(
    rooms: list[Room],
    required: list[str],
) -> list[Room]:
    """Отобрать переговорные с нужным оборудованием.

    Args:
        rooms: Список переговорных.
        required: Требуемое оборудование.

    Returns:
        Список подходящих комнат.
    """
    return [room for room in rooms if room.has_equipment(required)]


def sort_rooms(rooms: list[Room]) -> list[Room]:
    """Отсортировать переговорные по вместимости по убыванию.

    Args:
        rooms: Список переговорных.

    Returns:
        Новый список, отсортированный по capacity.
    """
    return sorted(rooms, key=lambda room: room.capacity, reverse=True)
