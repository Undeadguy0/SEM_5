"""Тесты для модуля bookings.py."""

from domain.bookings import (
    cancel_booking,
    create_booking,
    find_booking_by_id,
    find_bookings_by_organizer,
    get_booking_status,
    get_room_schedule,
    is_room_available,
)
from models import Booking, Room, User


def test_is_room_available_empty():
    bookings: list[Booking] = []
    assert is_room_available(bookings, 1, "2026-09-29") is True


def test_one_active_booking_per_room_and_date():
    bookings: list[Booking] = []
    room = Room(1, "Альфа", 8)
    other_room = Room(2, "Бета", 4)
    ivanov = User(1, "Иванов И.И.", "ivanov@example.com")
    petrov = User(2, "Петров П.П.", "petrov@example.com")

    first = create_booking(
        bookings,
        room,
        ivanov,
        "2026-09-29",
        "10:00",
        "11:00",
        "Планёрка",
    )
    assert first is not None
    assert is_room_available(bookings, 1, "2026-09-29") is False

    conflict = create_booking(
        bookings,
        room,
        petrov,
        "2026-09-29",
        "12:00",
        "13:00",
        "Совещание",
    )
    assert conflict is None
    assert len(bookings) == 1

    other_date = create_booking(
        bookings,
        room,
        petrov,
        "2026-09-30",
        "10:00",
        "11:00",
        "Другой день",
    )
    assert other_date is not None

    other = create_booking(
        bookings,
        other_room,
        petrov,
        "2026-09-29",
        "10:00",
        "11:00",
        "Другая комната",
    )
    assert other is not None

    assert first.cancel() is None
    assert first.is_cancelled is True
    assert len(bookings) == 3
    assert is_room_available(bookings, 1, "2026-09-29") is True

    again = create_booking(
        bookings,
        room,
        ivanov,
        "2026-09-29",
        "15:00",
        "16:00",
        "Повтор",
    )
    assert again is not None
    assert again.is_active() is True
    assert is_room_available(bookings, 1, "2026-09-29") is False


def test_create_booking_rejects_bad_interval():
    bookings: list[Booking] = []
    booking = create_booking(
        bookings,
        Room(1, "Альфа", 8),
        User(1, "Иванов И.И.", "ivanov@example.com"),
        "2026-09-29",
        "11:00",
        "10:00",
        "Планёрка",
    )
    assert booking is None
    assert bookings == []


def test_create_booking_fields():
    bookings: list[Booking] = []
    room = Room(1, "Альфа", 8)
    user = User(1, "Иванов И.И.", "ivanov@example.com")
    booking = create_booking(
        bookings,
        room,
        user,
        "2026-09-29",
        "10:00",
        "11:00",
        "Планёрка",
    )
    assert booking is not None
    assert booking.id == 1
    assert booking.room is room
    assert booking.user is user
    assert booking.booking_date == "2026-09-29"
    assert booking.start_time == "10:00"
    assert booking.end_time == "11:00"
    assert booking.topic == "Планёрка"


def test_cancel_booking_keeps_object():
    bookings: list[Booking] = []
    room = Room(1, "Альфа", 8)
    other = Room(2, "Бета", 4)
    ivanov = User(1, "Иванов И.И.", "ivanov@example.com")
    petrov = User(2, "Петров П.П.", "petrov@example.com")
    create_booking(
        bookings, room, ivanov, "2026-09-29", "10:00", "11:00", "Планёрка"
    )
    create_booking(
        bookings, other, petrov, "2026-09-29", "12:00", "13:00", "Совещание"
    )

    assert cancel_booking(bookings, 1) is True
    assert len(bookings) == 2
    assert bookings[0].is_cancelled is True
    assert bookings[1].id == 2
    assert bookings[1].is_active() is True

    assert cancel_booking(bookings, 999) is False
    assert len(bookings) == 2


def test_find_booking_by_id():
    bookings: list[Booking] = []
    room = Room(1, "Альфа", 8)
    user = User(1, "Иванов И.И.", "ivanov@example.com")
    created = create_booking(
        bookings,
        room,
        user,
        "2026-09-29",
        "10:00",
        "11:00",
        "Планёрка",
    )
    assert find_booking_by_id(bookings, 1) is created
    assert find_booking_by_id(bookings, 5) is None


def test_get_booking_status():
    assert get_booking_status(True) == "Переговорная свободна"
    assert get_booking_status(False) == "Переговорная уже занята"


def test_find_bookings_by_organizer():
    bookings: list[Booking] = []
    alpha = Room(1, "Альфа", 8)
    beta = Room(2, "Бета", 4)
    ivanov = User(1, "Иванов И.И.", "ivanov@example.com")
    petrov = User(2, "Петров П.П.", "petrov@example.com")
    create_booking(
        bookings, alpha, ivanov, "2026-09-29", "10:00", "11:00", "Планёрка"
    )
    create_booking(
        bookings, beta, petrov, "2026-09-29", "12:00", "13:00", "Совещание"
    )
    create_booking(
        bookings,
        alpha,
        ivanov,
        "2026-09-30",
        "10:00",
        "11:00",
        "Ретроспектива",
    )

    result = find_bookings_by_organizer(bookings, "Иванов")
    assert len(result) == 2
    for booking in result:
        assert "Иванов" in booking.user.name

    result = find_bookings_by_organizer(bookings, "петров")
    assert len(result) == 1

    result = find_bookings_by_organizer(bookings, "Сидоров")
    assert len(result) == 0


def test_get_room_schedule():
    room = Room(1, "Альфа", 8)
    other = Room(2, "Бета", 4)
    user = User(1, "Иванов И.И.", "ivanov@example.com")
    later = Booking(
        1, room, user, "2026-09-29", "14:00", "15:00", "Планёрка"
    )
    earlier = Booking(
        2, room, user, "2026-09-29", "10:00", "11:00", "Совещание"
    )
    another_room = Booking(
        3, other, user, "2026-09-29", "10:00", "11:00", "Встреча"
    )
    bookings = [later, earlier, another_room]

    schedule = get_room_schedule(bookings, 1, "2026-09-29")
    assert [item.start_time for item in schedule] == ["10:00", "14:00"]

    earlier.cancel()
    schedule = get_room_schedule(bookings, 1, "2026-09-29")
    assert [item.id for item in schedule] == [1]
    assert len(bookings) == 3

    schedule = get_room_schedule(bookings, 2, "2026-09-29")
    assert len(schedule) == 1

    schedule = get_room_schedule(bookings, 1, "2026-09-30")
    assert len(schedule) == 0
