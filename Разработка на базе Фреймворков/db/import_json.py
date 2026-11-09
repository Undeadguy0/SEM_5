"""Перенос данных Roomly из JSON в SQLite."""

import json
import sqlite3

from db.database import BASE_DIR, get_connection


ROOMS_FILE = BASE_DIR / "data" / "rooms.json"
USERS_FILE = BASE_DIR / "data" / "users.json"
BOOKINGS_FILE = BASE_DIR / "data" / "bookings.json"


def load_json(filename) -> list:
    """Прочитать список записей из JSON-файла.

    Args:
        filename: Путь к JSON-файлу.

    Returns:
        Список словарей.
    """
    with open(filename, encoding="utf-8") as file:
        return json.load(file)


def import_rooms(connection: sqlite3.Connection) -> None:
    """Загрузить помещения.

    Args:
        connection: Открытое соединение SQLite.
    """
    rooms = load_json(ROOMS_FILE)
    connection.executemany(
        """
        INSERT INTO rooms (
            id,
            name,
            capacity,
            equipment
        )
        VALUES (?, ?, ?, ?)
        """,
        [
            (
                room["id"],
                room["name"],
                room["capacity"],
                ", ".join(room.get("equipment") or []),
            )
            for room in rooms
        ],
    )


def import_users(connection: sqlite3.Connection) -> None:
    """Загрузить пользователей.

    Args:
        connection: Открытое соединение SQLite.
    """
    users = load_json(USERS_FILE)
    connection.executemany(
        """
        INSERT INTO users (
            id,
            name,
            email
        )
        VALUES (?, ?, ?)
        """,
        [
            (
                user["id"],
                user["name"],
                user["email"],
            )
            for user in users
        ],
    )


def import_bookings(connection: sqlite3.Connection) -> None:
    """Загрузить бронирования.

    Args:
        connection: Открытое соединение SQLite.
    """
    bookings = load_json(BOOKINGS_FILE)
    connection.executemany(
        """
        INSERT INTO bookings (
            id,
            room_id,
            user_id,
            booking_date,
            start_time,
            end_time,
            topic,
            is_cancelled
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                booking["id"],
                booking["room_id"],
                booking["user_id"],
                booking["booking_date"],
                booking["start_time"],
                booking["end_time"],
                booking["topic"],
                int(booking["is_cancelled"]),
            )
            for booking in bookings
        ],
    )


def main() -> None:
    """Очистить таблицы и заново перенести JSON.

    Сначала удаляются бронирования: на них ссылаются внешние ключи.
    """
    connection = get_connection()
    try:
        connection.execute("DELETE FROM bookings")
        connection.execute("DELETE FROM rooms")
        connection.execute("DELETE FROM users")
        import_rooms(connection)
        import_users(connection)
        import_bookings(connection)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    main()
