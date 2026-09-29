"""Модуль работы с бронированиями."""


def is_room_available(
    bookings: list[dict], room_id: int, date: str, start_time: str, end_time: str
) -> bool:
    """Проверить, свободна ли переговорная room_id в заданный временной слот.

    Args:
        bookings: Список бронирований.
        room_id: ID переговорной.
        date: Дата в формате YYYY-MM-DD.
        start_time: Время начала в формате HH:MM.
        end_time: Время окончания в формате HH:MM.

    Returns:
        True, если переговорная свободна, иначе False.
    """
    for booking in bookings:
        if booking["room_id"] == room_id and booking["date"] == date:
            if start_time < booking["end_time"] and end_time > booking["start_time"]:
                return False
    return True


def create_booking(
    bookings: list[dict],
    room_id: int,
    date: str,
    start_time: str,
    end_time: str,
    organizer: str,
    topic: str,
) -> dict | None:
    """Создать новое бронирование.

    Args:
        bookings: Список бронирований.
        room_id: ID переговорной.
        date: Дата в формате YYYY-MM-DD.
        start_time: Время начала в формате HH:MM.
        end_time: Время окончания в формате HH:MM.
        organizer: Организатор встречи.
        topic: Тема встречи.

    Returns:
        Созданное бронирование или None, если переговорная занята.
    """
    if not is_room_available(bookings, room_id, date, start_time, end_time):
        return None

    new_id = max((b["id"] for b in bookings), default=0) + 1
    booking = {
        "id": new_id,
        "room_id": room_id,
        "date": date,
        "start_time": start_time,
        "end_time": end_time,
        "organizer": organizer,
        "topic": topic,
    }
    bookings.append(booking)
    return booking


def cancel_booking(bookings: list[dict], booking_id: int) -> bool:
    """Отменить бронирование по его id.

    Args:
        bookings: Список бронирований.
        booking_id: ID бронирования для отмены.

    Returns:
        True, если бронирование найдено и удалено, иначе False.
    """
    for i, booking in enumerate(bookings):
        if booking["id"] == booking_id:
            bookings.pop(i)
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


def find_bookings_by_organizer(bookings: list[dict], organizer: str) -> list[dict]:
    """Найти все бронирования конкретного организатора.

    Args:
        bookings: Список бронирований.
        organizer: Имя организатора для поиска (нечувствительно к регистру).

    Returns:
        Список бронирований организатора.
    """
    organizer_lower = organizer.lower()
    return [booking for booking in bookings if organizer_lower in booking["organizer"].lower()]


def get_room_schedule(bookings: list[dict], room_id: int, date: str) -> list[dict]:
    """Получить расписание переговорной на указанную дату.

    Args:
        bookings: Список бронирований.
        room_id: ID переговорной.
        date: Дата в формате YYYY-MM-DD.

    Returns:
        Отсортированный по времени начала список бронирований.
    """
    room_bookings = [
        booking for booking in bookings if booking["room_id"] == room_id and booking["date"] == date
    ]
    return sorted(room_bookings, key=lambda x: x["start_time"])
