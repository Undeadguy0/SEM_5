"""Функции работы с бронированиями."""

from models import Booking, Room, User


def is_room_available(
    bookings: list[Booking],
    room_id: int,
    booking_date: str,
) -> bool:
    """Проверить, нет ли активного бронирования комнаты на дату.

    Отменённое бронирование комнату не занимает. На одну дату
    у комнаты может быть только одно активное бронирование.

    Args:
        bookings: Список бронирований.
        room_id: Идентификатор переговорной.
        booking_date: Дата в формате YYYY-MM-DD.

    Returns:
        True, если комната свободна на эту дату.
    """
    for booking in bookings:
        same_room = booking.room.id == room_id
        same_date = booking.booking_date == booking_date
        if same_room and same_date and booking.is_active():
            return False
    return True


def create_booking(
    bookings: list[Booking],
    room: Room,
    user: User,
    booking_date: str,
    start_time: str,
    end_time: str,
    topic: str,
) -> Booking | None:
    """Создать бронирование, если комната свободна на дату.

    Args:
        bookings: Список бронирований.
        room: Переговорная.
        user: Организатор.
        booking_date: Дата в формате YYYY-MM-DD.
        start_time: Время начала, HH:MM.
        end_time: Время окончания, HH:MM.
        topic: Тема встречи.

    Returns:
        Созданное бронирование или None, если дата занята
        или интервал времени некорректен.
    """
    if start_time >= end_time:
        return None
    if not is_room_available(bookings, room.id, booking_date):
        return None

    new_id = max((item.id for item in bookings), default=0) + 1
    booking = Booking(
        new_id,
        room,
        user,
        booking_date,
        start_time,
        end_time,
        topic,
    )
    bookings.append(booking)
    return booking


def cancel_booking(bookings: list[Booking], booking_id: int) -> bool:
    """Отменить бронирование по id, не удаляя его из списка.

    Args:
        bookings: Список бронирований.
        booking_id: Идентификатор бронирования.

    Returns:
        True, если запись найдена и отмечена отменённой.
    """
    for booking in bookings:
        if booking.id == booking_id:
            booking.cancel()
            return True
    return False


def get_booking_status(is_available: bool) -> str:
    """Вернуть текстовый статус переговорной (функция из ПР1).

    Args:
        is_available: Доступность переговорной.

    Returns:
        Текстовый статус.
    """
    if is_available:
        return "Переговорная свободна"
    return "Переговорная уже занята"


def find_bookings_by_organizer(
    bookings: list[Booking],
    organizer: str,
) -> list[Booking]:
    """Найти бронирования организатора по подстроке имени.

    Args:
        bookings: Список бронирований.
        organizer: Имя или его часть, без учёта регистра.

    Returns:
        Список бронирований этого организатора.
    """
    organizer_lower = organizer.lower()
    return [
        booking
        for booking in bookings
        if organizer_lower in booking.user.name.lower()
    ]


def get_room_schedule(
    bookings: list[Booking],
    room_id: int,
    booking_date: str,
) -> list[Booking]:
    """Получить активные бронирования переговорной на дату.

    Args:
        bookings: Список бронирований.
        room_id: Идентификатор переговорной.
        booking_date: Дата в формате YYYY-MM-DD.

    Returns:
        Активные бронирования, отсортированные по времени начала.
    """
    schedule = [
        booking
        for booking in bookings
        if booking.room.id == room_id
        and booking.booking_date == booking_date
        and booking.is_active()
    ]
    return sorted(schedule, key=lambda item: item.start_time)
