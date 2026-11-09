"""Перенос данных из базы ПР7 в таблицы Django ORM."""

import os
import sqlite3
import sys
from datetime import date
from pathlib import Path

import django
from django.db import connection as django_connection
from django.db import transaction


BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
SOURCE_DB = BASE_DIR / "data" / "roomly.sqlite"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "roomly.settings")
django.setup()

from bookings.models import Booking  # noqa: E402
from rooms.models import Room  # noqa: E402
from users.models import User  # noqa: E402


def _sync_sequence(model) -> None:
    """Сдвинуть счётчик SQLite за максимальный перенесённый id.

    Args:
        model: Модель Django, чьи идентификаторы сохранены.
    """
    table = model._meta.db_table
    max_pk = model.objects.order_by("-pk").values_list(
        "pk",
        flat=True,
    ).first() or 0
    with django_connection.cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM sqlite_master "
            "WHERE type = 'table' AND name = 'sqlite_sequence'",
        )
        if cursor.fetchone() is None:
            return
        cursor.execute(
            "UPDATE sqlite_sequence SET seq = %s WHERE name = %s",
            [max_pk, table],
        )
        if cursor.rowcount == 0:
            cursor.execute(
                "INSERT INTO sqlite_sequence (name, seq) "
                "VALUES (%s, %s)",
                [table, max_pk],
            )


def main() -> None:
    """Перенести помещения, пользователей и бронирования."""
    if not SOURCE_DB.exists():
        raise FileNotFoundError(
            f"Исходная база не найдена: {SOURCE_DB}"
        )
    with sqlite3.connect(SOURCE_DB) as source:
        source.row_factory = sqlite3.Row
        rooms = source.execute(
            """
            SELECT id, name, capacity, equipment
            FROM rooms
            ORDER BY id
            """
        ).fetchall()
        users = source.execute(
            """
            SELECT id, name, email
            FROM users
            ORDER BY id
            """
        ).fetchall()
        bookings = source.execute(
            """
            SELECT
                id,
                room_id,
                user_id,
                booking_date,
                start_time,
                end_time,
                topic,
                is_cancelled
            FROM bookings
            ORDER BY id
            """
        ).fetchall()

    with transaction.atomic():
        for row in rooms:
            Room.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "name": row["name"],
                    "capacity": row["capacity"],
                    "equipment": row["equipment"],
                },
            )
        for row in users:
            User.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "name": row["name"],
                    "email": row["email"],
                },
            )
        for row in bookings:
            Booking.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "room_id": row["room_id"],
                    "user_id": row["user_id"],
                    "booking_date": date.fromisoformat(
                        row["booking_date"],
                    ),
                    "start_time": row["start_time"],
                    "end_time": row["end_time"],
                    "topic": row["topic"],
                    "is_cancelled": bool(row["is_cancelled"]),
                },
            )
        _sync_sequence(Room)
        _sync_sequence(User)
        _sync_sequence(Booking)

    print("Перенос данных завершён.")
    print(f"Комнат: {Room.objects.count()}")
    print(f"Пользователей: {User.objects.count()}")
    print(f"Бронирований: {Booking.objects.count()}")


if __name__ == "__main__":
    main()
