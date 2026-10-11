"""Тесты сохранения и загрузки JSON."""

import json

from models import Booking, Room, User
from domain.rooms import add_room
from storage import (
    load_bookings,
    load_rooms,
    load_users,
    save_bookings,
    save_rooms,
    save_users,
)
from users import add_user


def test_rooms_roundtrip_keeps_id(tmp_path):
    filename = tmp_path / "rooms.json"
    rooms: list[Room] = []
    add_room(rooms, "Альфа", 8, ["доска"])
    save_rooms(str(filename), rooms)

    loaded = load_rooms(str(filename))
    assert loaded[0].id == 1
    assert loaded[0].name == "Альфа"
    assert loaded[0].capacity == 8
    assert loaded[0].equipment == ["доска"]

    raw = json.loads(filename.read_text(encoding="utf-8"))
    assert raw[0]["id"] == 1
    assert raw[0]["name"] == "Альфа"
    assert raw[0]["capacity"] == 8
    assert raw[0]["equipment"] == ["доска"]


def test_users_roundtrip(tmp_path):
    filename = tmp_path / "users.json"
    users: list[User] = []
    add_user(users, "Иванов И.И.", "ivanov@example.com")
    save_users(str(filename), users)

    loaded = load_users(str(filename))
    assert loaded[0].id == 1
    assert loaded[0].name == "Иванов И.И."
    assert loaded[0].email == "ivanov@example.com"

    raw = json.loads(filename.read_text(encoding="utf-8"))
    assert set(raw[0]) == {"id", "name", "email"}


def test_load_missing_files(tmp_path):
    assert load_rooms(str(tmp_path / "no-rooms.json")) == []
    assert load_users(str(tmp_path / "no-users.json")) == []
    assert (
        load_bookings(
            str(tmp_path / "no-bookings.json"),
            [],
            [],
        )
        == []
    )


def test_load_broken_json(tmp_path):
    rooms_file = tmp_path / "rooms.json"
    users_file = tmp_path / "users.json"
    bookings_file = tmp_path / "bookings.json"
    rooms_file.write_text("{broken", encoding="utf-8")
    users_file.write_text("{broken", encoding="utf-8")
    bookings_file.write_text("{broken", encoding="utf-8")
    assert load_rooms(str(rooms_file)) == []
    assert load_users(str(users_file)) == []
    assert load_bookings(str(bookings_file), [], []) == []


def test_load_wrong_shape(tmp_path):
    rooms_file = tmp_path / "rooms.json"
    users_file = tmp_path / "users.json"
    bookings_file = tmp_path / "bookings.json"
    rooms_file.write_text("{}", encoding="utf-8")
    users_file.write_text("{}", encoding="utf-8")
    bookings_file.write_text("{}", encoding="utf-8")
    assert load_rooms(str(rooms_file)) == []
    assert load_users(str(users_file)) == []
    assert load_bookings(str(bookings_file), [], []) == []


def test_bookings_roundtrip_links_objects(tmp_path):
    filename = tmp_path / "bookings.json"
    room = Room(1, "Альфа", 8, ["доска"])
    user = User(1, "Иванов И.И.", "ivanov@example.com")
    booking = Booking(
        1,
        room,
        user,
        "2026-09-29",
        "10:00",
        "11:30",
        "Планёрка",
        False,
    )
    save_bookings(str(filename), [booking])

    loaded = load_bookings(str(filename), [room], [user])
    assert len(loaded) == 1
    assert loaded[0].room is room
    assert loaded[0].user is user
    assert loaded[0].booking_date == "2026-09-29"
    assert loaded[0].topic == "Планёрка"
    assert loaded[0].is_cancelled is False

    raw = json.loads(filename.read_text(encoding="utf-8"))
    assert raw[0]["id"] == 1
    assert raw[0]["room_id"] == 1
    assert raw[0]["user_id"] == 1
    assert raw[0]["booking_date"] == "2026-09-29"
    assert raw[0]["is_cancelled"] is False


def test_load_bookings_skips_missing_links(tmp_path):
    filename = tmp_path / "bookings.json"
    room = Room(1, "Альфа", 8)
    user = User(1, "Иванов И.И.", "ivanov@example.com")
    filename.write_text(
        json.dumps(
            [
                {
                    "id": 1,
                    "room_id": 99,
                    "user_id": 1,
                    "booking_date": "2026-09-29",
                    "start_time": "10:00",
                    "end_time": "11:00",
                    "topic": "Нет комнаты",
                    "is_cancelled": False,
                },
                {
                    "id": 2,
                    "room_id": 1,
                    "user_id": 99,
                    "booking_date": "2026-09-29",
                    "start_time": "12:00",
                    "end_time": "13:00",
                    "topic": "Нет пользователя",
                    "is_cancelled": False,
                },
                {
                    "id": 3,
                    "room_id": 1,
                    "user_id": 1,
                    "booking_date": "2026-09-30",
                    "start_time": "12:00",
                    "end_time": "13:00",
                    "topic": "Нормальная",
                    "is_cancelled": False,
                },
            ]
        ),
        encoding="utf-8",
    )
    loaded = load_bookings(str(filename), [room], [user])
    assert len(loaded) == 1
    assert loaded[0].id == 3
    assert loaded[0].room is room
    assert loaded[0].user is user
