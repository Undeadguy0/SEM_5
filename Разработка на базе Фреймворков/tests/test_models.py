"""Тесты классов Room, User и Booking."""

from models import Booking, Room, User


def test_room_attributes_and_methods():
    room = Room(1, "Переговорная «Альфа»", 8, ["Проектор", "доска"])
    assert room.id == 1
    assert room.name == "Переговорная «Альфа»"
    assert room.capacity == 8
    assert room.is_suitable_for(8) is True
    assert room.is_suitable_for(9) is False
    assert room.has_equipment(["проектор"]) is True
    assert room.has_equipment(["проектор", "доска"]) is True
    assert room.has_equipment(["телефон"]) is False
    assert str(room) == "Переговорная «Альфа», 8 мест"


def test_room_from_data_and_to_dict():
    source = {
        "id": 3,
        "name": "Гамма",
        "capacity": 12,
        "equipment": ["проектор"],
    }
    room = Room.from_data(source)
    assert room.id == 3
    assert room.capacity == 12
    assert room.to_dict() == source
    source["equipment"].append("доска")
    assert room.equipment == ["проектор"]


def test_room_without_equipment():
    room = Room(2, "Бета", 4)
    assert room.equipment == []
    assert room.has_equipment([]) is True
    assert str(room) == "Бета, 4 мест"


def test_user_from_data_and_str():
    user = User.from_data(
        {"id": 1, "name": "Иванов И.И.", "email": "ivanov@example.com"}
    )
    assert user.id == 1
    assert user.name == "Иванов И.И."
    assert user.email == "ivanov@example.com"
    assert user.to_dict()["email"] == "ivanov@example.com"
    assert str(user) == "Иванов И.И. <ivanov@example.com>"


def test_booking_links_objects_and_cancel():
    room = Room(1, "Альфа", 8, ["доска"])
    user = User(1, "Иванов И.И.", "ivanov@example.com")
    booking = Booking(
        5,
        room,
        user,
        "2026-09-29",
        "10:00",
        "11:30",
        "Планёрка",
    )
    assert booking.room is room
    assert booking.user is user
    assert booking.is_cancelled is False
    assert booking.is_active() is True
    assert "активно" in str(booking)
    assert booking.room.name in str(booking)

    booking.cancel()
    assert booking.is_cancelled is True
    assert booking.is_active() is False
    assert "отменено" in str(booking)
    assert booking.to_dict()["room_id"] == 1
    assert booking.to_dict()["user_id"] == 1
    assert booking.to_dict()["is_cancelled"] is True
