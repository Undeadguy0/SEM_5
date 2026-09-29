"""Точка входа, меню приложения."""

from bookings import (
    cancel_booking,
    create_booking,
    find_bookings_by_organizer,
    get_booking_status,
    get_room_schedule,
    is_room_available,
)
from rooms import (
    filter_rooms_by_capacity,
    filter_rooms_by_equipment,
    find_room,
    sort_rooms,
)
from storage import load_bookings, load_rooms, save_bookings
from utils import input_date, input_int, input_time

ROOMS_FILE = "data/rooms.json"
BOOKINGS_FILE = "data/bookings.json"


def show_rooms(rooms: dict[int, dict]) -> None:
    """Вывести список переговорных в виде таблицы.

    Args:
        rooms: Словарь переговорных комнат.
    """
    if not rooms:
        print("Переговорных комнат нет.")
        return

    print(f"{'ID':<4} {'Название':<30} {'Вместимость':<12} Оборудование")
    print("-" * 70)
    for room_id, room in rooms.items():
        equipment = ", ".join(room["equipment"]) if room["equipment"] else "—"
        print(f"{room_id:<4} {room['name']:<30} " f"{room['capacity']:<12} {equipment}")


def show_bookings(bookings: list[dict]) -> None:
    """Вывести список бронирований.

    Args:
        bookings: Список бронирований.
    """
    if not bookings:
        print("Бронирований нет.")
        return

    print(f"{'ID':<4} {'Комната':<8} {'Дата':<12} " f"{'Время':<13} {'Организатор':<20} Тема")
    print("-" * 90)
    for booking in bookings:
        time_str = f"{booking['start_time']}-{booking['end_time']}"
        print(
            f"{booking['id']:<4} {booking['room_id']:<8} "
            f"{booking['date']:<12} {time_str:<13} "
            f"{booking['organizer']:<20} {booking['topic']}"
        )


def rooms_by_id(room_list: list[dict]) -> dict[int, dict]:
    """Собрать словарь переговорных из списка, сохранив порядок.

    Args:
        room_list: Список записей, в каждой есть ключ id.

    Returns:
        Словарь {id: данные комнаты}.
    """
    return {room["id"]: room for room in room_list}


def input_existing_room_id(rooms: dict[int, dict]) -> int | None:
    """Запросить id существующей переговорной.

    Args:
        rooms: Словарь переговорных комнат.

    Returns:
        id комнаты или None, если такой комнаты нет.
    """
    room_id = input_int("ID переговорной: ")
    if room_id not in rooms:
        print("Переговорная не найдена.")
        return None
    return room_id


def input_time_slot() -> tuple[str, str, str] | None:
    """Запросить дату и интервал времени.

    Returns:
        Кортеж (дата, начало, конец) или None, если интервал некорректен.
    """
    date = input_date("Дата (DD.MM.YYYY): ")
    start = input_time("Время начала (HH:MM): ")
    end = input_time("Время окончания (HH:MM): ")
    if start >= end:
        print("Ошибка: время начала должно быть раньше времени окончания.")
        return None
    return date, start, end


def menu_show_all_rooms(rooms: dict[int, dict]) -> None:
    """Показать все переговорные."""
    print("\n=== Все переговорные ===")
    show_rooms(rooms_by_id(sort_rooms(rooms)))


def menu_find_by_name(rooms: dict[int, dict]) -> None:
    """Найти переговорную по названию."""
    query = input("Введите часть названия: ").strip()
    results = find_room(rooms, query)
    print(f"\nНайдено: {len(results)}")
    if results:
        show_rooms(rooms_by_id(results))


def menu_find_by_capacity(rooms: dict[int, dict]) -> None:
    """Найти переговорные по вместимости."""
    min_cap = input_int("Минимальная вместимость: ")
    results = filter_rooms_by_capacity(rooms, min_cap)
    print(f"\nНайдено: {len(results)}")
    if results:
        show_rooms(rooms_by_id(results))


def menu_find_by_equipment(rooms: dict[int, dict]) -> None:
    """Найти переговорные по оборудованию."""
    query = input("Введите оборудование через запятую: ").strip()
    required = [item.strip() for item in query.split(",") if item.strip()]
    results = filter_rooms_by_equipment(rooms, required)
    print(f"\nНайдено: {len(results)}")
    if results:
        show_rooms(rooms_by_id(results))


def menu_check_availability(rooms: dict[int, dict], bookings: list[dict]) -> None:
    """Проверить доступность переговорной."""
    room_id = input_existing_room_id(rooms)
    if room_id is None:
        return

    slot = input_time_slot()
    if slot is None:
        return
    date, start, end = slot

    available = is_room_available(bookings, room_id, date, start, end)
    status = get_booking_status(available)
    print(f"\n{rooms[room_id]['name']} на {date} {start}-{end}: {status}")


def menu_create_booking(rooms: dict[int, dict], bookings: list[dict]) -> None:
    """Забронировать переговорную."""
    room_id = input_existing_room_id(rooms)
    if room_id is None:
        return

    slot = input_time_slot()
    if slot is None:
        return
    date, start, end = slot

    if not is_room_available(bookings, room_id, date, start, end):
        print(get_booking_status(False))
        return

    organizer = input("Организатор: ").strip()
    if not organizer:
        print("Организатор не может быть пустым.")
        return

    topic = input("Тема встречи: ").strip()
    if not topic:
        print("Тема не может быть пустой.")
        return

    booking = create_booking(bookings, room_id, date, start, end, organizer, topic)
    if booking:
        save_bookings(BOOKINGS_FILE, bookings)
        print(f"Бронирование создано (ID: {booking['id']}).")
    else:
        print("Не удалось создать бронирование.")


def menu_cancel_booking(bookings: list[dict]) -> None:
    """Отменить бронирование."""
    booking_id = input_int("ID бронирования для отмены: ")
    if cancel_booking(bookings, booking_id):
        save_bookings(BOOKINGS_FILE, bookings)
        print("Бронирование отменено.")
    else:
        print("Бронирование не найдено.")


def menu_show_all_bookings(bookings: list[dict]) -> None:
    """Показать все бронирования."""
    print("\n=== Все бронирования ===")
    show_bookings(bookings)


def menu_room_schedule(rooms: dict[int, dict], bookings: list[dict]) -> None:
    """Расписание переговорной на дату."""
    room_id = input_existing_room_id(rooms)
    if room_id is None:
        return

    date = input_date("Дата (DD.MM.YYYY): ")
    schedule = get_room_schedule(bookings, room_id, date)
    print(f"\nРасписание {rooms[room_id]['name']} на {date}:")
    if schedule:
        show_bookings(schedule)
    else:
        print("Бронирований на эту дату нет.")


def menu_my_bookings(bookings: list[dict]) -> None:
    """Мои бронирования (по организатору)."""
    organizer = input("Имя организатора: ").strip()
    results = find_bookings_by_organizer(bookings, organizer)
    print(f"\nБронирований организатора '{organizer}': {len(results)}")
    if results:
        show_bookings(results)


def main() -> None:
    """Точка запуска приложения."""
    rooms = load_rooms(ROOMS_FILE)
    bookings = load_bookings(BOOKINGS_FILE)

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
            lambda: menu_create_booking(rooms, bookings),
        ),
        "7": (
            "Отменить бронирование",
            lambda: menu_cancel_booking(bookings),
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
        for key, (desc, _) in menu_items.items():
            print(f"{key}. {desc}")
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
