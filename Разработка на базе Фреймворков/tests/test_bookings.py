"""Тесты для модуля bookings.py."""

from bookings import (
    cancel_booking,
    create_booking,
    find_bookings_by_organizer,
    get_booking_status,
    get_room_schedule,
    is_room_available,
)


def test_is_room_available_empty():
    bookings = []
    assert is_room_available(bookings, 1, "2026-09-29", "10:00", "11:00") is True


def test_is_room_available_overlap():
    bookings = []
    create_booking(
        bookings,
        1,
        "2026-09-29",
        "10:00",
        "11:00",
        "Иванов И.И.",
        "Планёрка",
    )

    # Пересекающийся слот (начало в середине)
    assert is_room_available(bookings, 1, "2026-09-29", "10:30", "11:30") is False

    # Пересекающийся слот (окончание в середине)
    assert is_room_available(bookings, 1, "2026-09-29", "09:30", "10:30") is False

    # Полностью внутри
    assert is_room_available(bookings, 1, "2026-09-29", "10:15", "10:45") is False

    # Полностью снаружи (после)
    assert is_room_available(bookings, 1, "2026-09-29", "11:00", "12:00") is True

    # Полностью снаружи (до)
    assert is_room_available(bookings, 1, "2026-09-29", "09:00", "10:00") is True

    # Другая комната — доступна
    assert is_room_available(bookings, 2, "2026-09-29", "10:00", "11:00") is True

    # Другая дата — доступна
    assert is_room_available(bookings, 1, "2026-09-30", "10:00", "11:00") is True


def test_create_booking():
    bookings = []
    booking = create_booking(
        bookings,
        1,
        "2026-09-29",
        "10:00",
        "11:00",
        "Иванов И.И.",
        "Планёрка",
    )
    assert booking is not None
    assert booking["id"] == 1
    assert booking["room_id"] == 1
    assert booking["date"] == "2026-09-29"
    assert booking["start_time"] == "10:00"
    assert booking["end_time"] == "11:00"
    assert booking["organizer"] == "Иванов И.И."
    assert booking["topic"] == "Планёрка"
    assert len(bookings) == 1

    # Попытка создать пересекающееся бронирование
    booking2 = create_booking(
        bookings,
        1,
        "2026-09-29",
        "10:30",
        "11:30",
        "Петров П.П.",
        "Совещание",
    )
    assert booking2 is None
    assert len(bookings) == 1


def test_cancel_booking():
    bookings = []
    create_booking(
        bookings,
        1,
        "2026-09-29",
        "10:00",
        "11:00",
        "Иванов И.И.",
        "Планёрка",
    )
    create_booking(
        bookings,
        2,
        "2026-09-29",
        "12:00",
        "13:00",
        "Петров П.П.",
        "Совещание",
    )

    # Отмена существующего
    assert cancel_booking(bookings, 1) is True
    assert len(bookings) == 1
    assert bookings[0]["id"] == 2

    # Отмена несуществующего
    assert cancel_booking(bookings, 999) is False
    assert len(bookings) == 1


def test_get_booking_status():
    assert get_booking_status(True) == "Переговорная свободна"
    assert get_booking_status(False) == "Переговорная уже занята"


def test_find_bookings_by_organizer():
    bookings = []
    create_booking(
        bookings,
        1,
        "2026-09-29",
        "10:00",
        "11:00",
        "Иванов И.И.",
        "Планёрка",
    )
    create_booking(
        bookings,
        2,
        "2026-09-29",
        "12:00",
        "13:00",
        "Петров П.П.",
        "Совещание",
    )
    create_booking(
        bookings,
        1,
        "2026-09-30",
        "10:00",
        "11:00",
        "Иванов И.И.",
        "Ретроспектива",
    )

    result = find_bookings_by_organizer(bookings, "Иванов")
    assert len(result) == 2
    for booking in result:
        assert "Иванов" in booking["organizer"]

    result = find_bookings_by_organizer(bookings, "петров")
    assert len(result) == 1

    result = find_bookings_by_organizer(bookings, "Сидоров")
    assert len(result) == 0


def test_get_room_schedule():
    bookings = []
    create_booking(
        bookings,
        1,
        "2026-09-29",
        "14:00",
        "15:00",
        "Иванов И.И.",
        "Планёрка",
    )
    create_booking(
        bookings,
        1,
        "2026-09-29",
        "10:00",
        "11:00",
        "Петров П.П.",
        "Совещание",
    )
    create_booking(
        bookings,
        2,
        "2026-09-29",
        "10:00",
        "11:00",
        "Сидоров С.С.",
        "Встреча",
    )

    schedule = get_room_schedule(bookings, 1, "2026-09-29")
    assert len(schedule) == 2
    assert schedule[0]["start_time"] == "10:00"
    assert schedule[1]["start_time"] == "14:00"

    schedule = get_room_schedule(bookings, 2, "2026-09-29")
    assert len(schedule) == 1

    schedule = get_room_schedule(bookings, 1, "2026-09-30")
    assert len(schedule) == 0
