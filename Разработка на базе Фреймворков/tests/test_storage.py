"""Тесты сохранения и загрузки JSON."""

import json

from rooms import add_room
from storage import load_bookings, load_rooms, save_bookings, save_rooms


def test_rooms_roundtrip_keeps_id(tmp_path):
    filename = tmp_path / "rooms.json"
    rooms: dict[int, dict] = {}
    add_room(rooms, "Альфа", 8, ["доска"])
    save_rooms(str(filename), rooms)

    loaded = load_rooms(str(filename))
    assert loaded[1]["name"] == "Альфа"
    assert loaded[1]["capacity"] == 8
    assert "id" not in loaded[1]

    raw = json.loads(filename.read_text(encoding="utf-8"))
    assert raw[0]["id"] == 1
    assert raw[0]["equipment"] == ["доска"]


def test_load_missing_files(tmp_path):
    assert load_rooms(str(tmp_path / "no-rooms.json")) == {}
    assert load_bookings(str(tmp_path / "no-bookings.json")) == []


def test_load_broken_json(tmp_path):
    rooms_file = tmp_path / "rooms.json"
    bookings_file = tmp_path / "bookings.json"
    rooms_file.write_text("{broken", encoding="utf-8")
    bookings_file.write_text("{broken", encoding="utf-8")
    assert load_rooms(str(rooms_file)) == {}
    assert load_bookings(str(bookings_file)) == []


def test_load_wrong_shape(tmp_path):
    rooms_file = tmp_path / "rooms.json"
    bookings_file = tmp_path / "bookings.json"
    rooms_file.write_text("{}", encoding="utf-8")
    bookings_file.write_text("{}", encoding="utf-8")
    assert load_rooms(str(rooms_file)) == {}
    assert load_bookings(str(bookings_file)) == []


def test_bookings_roundtrip(tmp_path):
    filename = tmp_path / "bookings.json"
    bookings = [
        {
            "id": 1,
            "room_id": 1,
            "date": "2026-09-29",
            "start_time": "10:00",
            "end_time": "11:30",
            "organizer": "Иванов И.И.",
            "topic": "Планёрка",
        }
    ]
    save_bookings(str(filename), bookings)
    assert load_bookings(str(filename)) == bookings
