"""Точка входа и меню приложения."""

from bookings import (
    cancel_booking,
    create_booking,
    find_bookings_by_organizer,
    get_booking_status,
    get_room_schedule,
    is_room_available,
)
from models import Booking, Room, User
from rooms import (
    filter_rooms_by_capacity,
    filter_rooms_by_equipment,
    find_room,
    get_room_by_id,
    sort_rooms,
)
from storage import (
    load_bookings,
    load_rooms,
    load_users,
    save_bookings,
    save_users,
)
from users import add_user, find_user_by_name
from utils import input_date, input_int, input_time

ROOMS_FILE = "data/rooms.json"
USERS_FILE = "data/users.json"
BOOKINGS_FILE = "data/bookings.json"


def show_rooms(rooms: list[Room]) -> None:
    """Вывести список переговорных в виде таблицы.

    Args:
        rooms: Список переговорных.
    """
    if not rooms:
        print("Переговорных комнат нет.")
        return

    print(
        f"{'ID':<4} {'Название':<30} "
        f"{'Вместимость':<12} Оборудование"
    )
    print("-" * 70)
    for room in rooms:
        if room.equipment:
            equipment = ", ".join(room.equipment)
        else:
            equipment = "—"
        print(
            f"{room.id:<4} {room.name:<30} "
            f"{room.capacity:<12} {equipment}"
        )


def show_bookings(bookings: list[Booking]) -> None:
    """Вывести список бронирований.

    Args:
        bookings: Список бронирований.
    """
    if not bookings:
        print("Бронирований нет.")
        return

    print(
        f"{'ID':<4} {'Комната':<24} {'Дата':<12} "
        f"{'Время':<13} {'Организатор':<16} {'Статус':<10} Тема"
    )
    print("-" * 110)
    for booking in bookings:
        time_str = f"{booking.start_time}-{booking.end_time}"
        if booking.is_cancelled:
            status = "отменено"
        else:
            status = "активно"
        print(
            f"{booking.id:<4} {booking.room.name:<24} "
            f"{booking.booking_date:<12} {time_str:<13} "
            f"{booking.user.name:<16} {status:<10} "
            f"{booking.topic}"
        )


def input_existing_room_id(rooms: list[Room]) -> Room | None:
    """Запросить id существующей переговорной.

    Args:
        rooms: Список переговорных.

    Returns:
        Объект Room или None, если такой комнаты нет.
    """
    room_id = input_int("ID переговорной: ")
    room = get_room_by_id(rooms, room_id)
    if room is None:
        print("Переговорная не найдена.")
        return None
    return room


def input_time_slot() -> tuple[str, str, str] | None:
    """Запросить дату и интервал времени.

    Returns:
        Кортеж (дата, начало, конец) или None,
        если интервал некорректен.
    """
    booking_date = input_date("Дата (DD.MM.YYYY): ")
    start = input_time("Время начала (HH:MM): ")
    end = input_time("Время окончания (HH:MM): ")
    if start >= end:
        print("Ошибка: время начала должно быть раньше окончания.")
        return None
    return booking_date, start, end


def input_new_email() -> str:
    """Запросить email, повторяя ввод при ошибке.

    Returns:
        Непустой email, содержащий символ @.
    """
    while True:
        email = input("Email нового организатора: ").strip()
        missing_at = "@" not in email
        bad_edges = email.startswith("@") or email.endswith("@")
        if missing_at or bad_edges:
            print("Ошибка: укажите email, например user@example.com.")
            continue
        return email


def ask_organizer(users: list[User]) -> User | None:
    """Найти организатора по имени или создать нового пользователя.

    Args:
        users: Список пользователей.

    Returns:
        Объект User или None, если имя пустое.
    """
    name = input("Организатор: ").strip()
    if not name:
        print("Организатор не может быть пустым.")
        return None

    existing = find_user_by_name(users, name)
    if existing is not None:
        print(f"Организатор: {existing}")
        return existing

    email = input_new_email()
    user = add_user(users, name, email)
    save_users(USERS_FILE, users)
    print(f"Создан пользователь: {user}")
    return user


def menu_show_all_rooms(rooms: list[Room]) -> None:
    """Показать все переговорные, отсортированные по вместимости."""
    print("\n=== Все переговорные ===")
    show_rooms(sort_rooms(rooms))


def menu_find_by_name(rooms: list[Room]) -> None:
    """Найти переговорную по названию."""
    query = input("Введите часть названия: ").strip()
    results = find_room(rooms, query)
    print(f"\nНайдено: {len(results)}")
    if results:
        show_rooms(results)


def menu_find_by_capacity(rooms: list[Room]) -> None:
    """Найти переговорные по вместимости."""
    min_cap = input_int("Минимальная вместимость: ")
    results = filter_rooms_by_capacity(rooms, min_cap)
    print(f"\nНайдено: {len(results)}")
    if results:
        show_rooms(results)


def menu_find_by_equipment(rooms: list[Room]) -> None:
    """Найти переговорные по оборудованию."""
    query = input("Введите оборудование через запятую: ").strip()
    required = [
        item.strip()
        for item in query.split(",")
        if item.strip()
    ]
    results = filter_rooms_by_equipment(rooms, required)
    print(f"\nНайдено: {len(results)}")
    if results:
        show_rooms(results)


def menu_check_availability(
    rooms: list[Room],
    bookings: list[Booking],
) -> None:
    """Проверить, свободна ли переговорная на дату."""
    room = input_existing_room_id(rooms)
    if room is None:
        return

    booking_date = input_date("Дата (DD.MM.YYYY): ")
    available = is_room_available(bookings, room.id, booking_date)
    status = get_booking_status(available)
    print(f"\n{room} на {booking_date}: {status}")


def create_new_booking(
    rooms: list[Room],
    users: list[User],
    bookings: list[Booking],
) -> None:
    """Создать бронирование через диалог с пользователем.

    Args:
        rooms: Список переговорных.
        users: Список пользователей.
        bookings: Список бронирований.
    """
    room = input_existing_room_id(rooms)
    if room is None:
        return

    slot = input_time_slot()
    if slot is None:
        return
    booking_date, start, end = slot

    if not is_room_available(bookings, room.id, booking_date):
        print(get_booking_status(False))
        print("На эту дату уже есть активное бронирование.")
        return

    organizer = ask_organizer(users)
    if organizer is None:
        return

    topic = input("Тема встречи: ").strip()
    if not topic:
        print("Тема не может быть пустой.")
        return

    booking = create_booking(
        bookings,
        room,
        organizer,
        booking_date,
        start,
        end,
        topic,
    )
    if booking is None:
        print("Не удалось создать бронирование.")
        return

    save_bookings(BOOKINGS_FILE, bookings)
    print(f"Бронирование создано: {booking}")


def cancel_existing_booking(bookings: list[Booking]) -> None:
    """Отменить бронирование по id.

    Args:
        bookings: Список бронирований.
    """
    booking_id = input_int("ID бронирования для отмены: ")
    if cancel_booking(bookings, booking_id):
        save_bookings(BOOKINGS_FILE, bookings)
        print("Бронирование отменено.")
        return
    print("Бронирование не найдено.")


def menu_show_all_bookings(bookings: list[Booking]) -> None:
    """Показать все бронирования."""
    print("\n=== Все бронирования ===")
    show_bookings(bookings)


def menu_room_schedule(
    rooms: list[Room],
    bookings: list[Booking],
) -> None:
    """Показать расписание переговорной на дату."""
    room = input_existing_room_id(rooms)
    if room is None:
        return

    booking_date = input_date("Дата (DD.MM.YYYY): ")
    schedule = get_room_schedule(bookings, room.id, booking_date)
    print(f"\nРасписание: {room.name} на {booking_date}")
    if schedule:
        show_bookings(schedule)
        return
    print("Бронирований на эту дату нет.")


def menu_my_bookings(bookings: list[Booking]) -> None:
    """Показать бронирования организатора."""
    organizer = input("Имя организатора: ").strip()
    found = find_bookings_by_organizer(bookings, organizer)
    print(f"\nБронирований организатора «{organizer}»: {len(found)}")
    if found:
        show_bookings(found)


def main() -> None:
    """Точка запуска приложения."""
    rooms = load_rooms(ROOMS_FILE)
    users = load_users(USERS_FILE)
    bookings = load_bookings(BOOKINGS_FILE, rooms, users)

    menu_items = {
        "1": (
            "Показать все переговорные",
            lambda: menu_show_all_rooms(rooms),
        ),
        "2": (
            "Найти переговорную по названию",
            lambda: menu_find_by_name(rooms),
        ),
        "3": (
            "Найти переговорные по вместимости",
            lambda: menu_find_by_capacity(rooms),
        ),
        "4": (
            "Найти переговорные по оборудованию",
            lambda: menu_find_by_equipment(rooms),
        ),
        "5": (
            "Проверить доступность переговорной",
            lambda: menu_check_availability(rooms, bookings),
        ),
        "6": (
            "Забронировать переговорную",
            lambda: create_new_booking(rooms, users, bookings),
        ),
        "7": (
            "Отменить бронирование",
            lambda: cancel_existing_booking(bookings),
        ),
        "8": (
            "Показать все бронирования",
            lambda: menu_show_all_bookings(bookings),
        ),
        "9": (
            "Расписание переговорной на дату",
            lambda: menu_room_schedule(rooms, bookings),
        ),
        "10": (
            "Мои бронирования (по организатору)",
            lambda: menu_my_bookings(bookings),
        ),
    }

    while True:
        print("\n=== Система бронирования переговорных комнат ===")
        for key, (description, _) in menu_items.items():
            print(f"{key}. {description}")
        print("0. Выход")

        choice = input("\nВыберите действие: ").strip()
        if choice == "0":
            print("До свидания!")
            break
        if choice in menu_items:
            menu_items[choice][1]()
        else:
            print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()
