"""Тесты для модуля rooms.py."""

from rooms import (
    add_room,
    check_room_capacity,
    filter_rooms_by_capacity,
    filter_rooms_by_equipment,
    find_room,
    sort_rooms,
)


def test_add_room():
    rooms = {}
    add_room(rooms, "Переговорная «Альфа»", 8, ["проектор", "доска"])
    assert len(rooms) == 1
    assert rooms[1]["capacity"] == 8
    assert rooms[1]["name"] == "Переговорная «Альфа»"
    assert rooms[1]["equipment"] == ["проектор", "доска"]


def test_find_room():
    rooms = {}
    add_room(rooms, "Переговорная «Альфа»", 8, [])
    add_room(rooms, "Переговорная «Бета»", 4, [])
    result = find_room(rooms, "альфа")
    assert len(result) == 1
    assert result[0]["name"] == "Переговорная «Альфа»"

    # Поиск части названия
    result = find_room(rooms, "переговорная")
    assert len(result) == 2

    # Ничего не найдено
    result = find_room(rooms, "гамма")
    assert len(result) == 0


def test_check_room_capacity():
    rooms = {}
    add_room(rooms, "Переговорная «Альфа»", 8, [])
    assert check_room_capacity(rooms, 1, 6) is True
    assert check_room_capacity(rooms, 1, 8) is True
    assert check_room_capacity(rooms, 1, 10) is False
    # Несуществующая комната
    assert check_room_capacity(rooms, 999, 5) is False


def test_filter_rooms_by_equipment():
    rooms = {}
    add_room(rooms, "Альфа", 8, ["проектор", "доска"])
    add_room(rooms, "Бета", 4, ["доска"])
    add_room(rooms, "Гамма", 12, ["проектор", "видеосвязь", "телефон"])

    # Одно оборудование
    result = filter_rooms_by_equipment(rooms, ["проектор"])
    assert len(result) == 2
    names = {r["name"] for r in result}
    assert names == {"Альфа", "Гамма"}

    # Несколько оборудований
    result = filter_rooms_by_equipment(rooms, ["проектор", "доска"])
    assert len(result) == 1
    assert result[0]["name"] == "Альфа"

    # Пустой список требований
    result = filter_rooms_by_equipment(rooms, [])
    assert len(result) == 3

    # Несуществующее оборудование
    result = filter_rooms_by_equipment(rooms, ["кофемашина"])
    assert len(result) == 0


def test_filter_rooms_by_capacity():
    rooms = {}
    add_room(rooms, "Альфа", 8, [])
    add_room(rooms, "Бета", 4, [])
    add_room(rooms, "Гамма", 12, [])

    result = filter_rooms_by_capacity(rooms, 6)
    assert len(result) == 2
    names = {r["name"] for r in result}
    assert names == {"Альфа", "Гамма"}

    result = filter_rooms_by_capacity(rooms, 12)
    assert len(result) == 1
    assert result[0]["name"] == "Гамма"

    result = filter_rooms_by_capacity(rooms, 15)
    assert len(result) == 0


def test_sort_rooms():
    rooms = {}
    add_room(rooms, "Бета", 4, [])
    add_room(rooms, "Альфа", 8, [])
    add_room(rooms, "Гамма", 12, [])

    result = sort_rooms(rooms)
    assert len(result) == 3
    assert result[0]["name"] == "Гамма"  # capacity 12
    assert result[1]["name"] == "Альфа"  # capacity 8
    assert result[2]["name"] == "Бета"  # capacity 4
