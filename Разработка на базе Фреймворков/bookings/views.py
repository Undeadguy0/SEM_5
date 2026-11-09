"""Страницы бронирований."""

from contextlib import closing

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db.database import get_connection
from homepage.views import http_not_found


def bookings(request: HttpRequest) -> HttpResponse:
    """Показать активные бронирования с помещением и организатором."""
    with closing(get_connection()) as connection:
        booking_list = connection.execute(
            """
            SELECT
                bookings.id,
                bookings.booking_date,
                bookings.start_time,
                bookings.end_time,
                bookings.topic,
                bookings.is_cancelled,
                rooms.name AS room_name,
                users.name AS user_name
            FROM bookings
            JOIN rooms
                ON bookings.room_id = rooms.id
            JOIN users
                ON bookings.user_id = users.id
            WHERE bookings.is_cancelled = 0
            ORDER BY bookings.booking_date, bookings.start_time;
            """
        ).fetchall()
    context = {"bookings": booking_list}
    return render(request, "bookings/booking_list.html", context)


def booking_detail(
    request: HttpRequest,
    booking_id: int,
) -> HttpResponse:
    """Показать карточку одного бронирования."""
    with closing(get_connection()) as connection:
        booking = connection.execute(
            """
            SELECT
                bookings.id,
                bookings.room_id,
                bookings.booking_date,
                bookings.start_time,
                bookings.end_time,
                bookings.topic,
                bookings.is_cancelled,
                rooms.name AS room_name,
                users.name AS user_name,
                users.email AS user_email
            FROM bookings
            JOIN rooms
                ON bookings.room_id = rooms.id
            JOIN users
                ON bookings.user_id = users.id
            WHERE bookings.id = ?;
            """,
            (booking_id,),
        ).fetchone()
    if booking is None:
        return http_not_found(
            request,
            "Бронирование не найдено.",
            "bookings:bookings",
            "К списку бронирований",
        )
    context = {"booking": booking}
    return render(request, "bookings/booking_detail.html", context)


def statistics(request: HttpRequest) -> HttpResponse:
    """Показать сводку, группировки и отбор групп по числу броней."""
    with closing(get_connection()) as connection:
        bookings_count = connection.execute(
            """
            SELECT COUNT(*) AS bookings_count
            FROM bookings
            WHERE is_cancelled = 0;
            """
        ).fetchone()["bookings_count"]
        summary = connection.execute(
            """
            SELECT
                COUNT(*) AS rooms_count,
                AVG(capacity) AS average_capacity,
                MAX(capacity) AS max_capacity
            FROM rooms;
            """
        ).fetchone()
        by_room = connection.execute(
            """
            SELECT
                rooms.name AS room_name,
                COUNT(bookings.id) AS bookings_count
            FROM rooms
            LEFT JOIN bookings
                ON rooms.id = bookings.room_id
                AND bookings.is_cancelled = 0
            GROUP BY rooms.id, rooms.name
            ORDER BY bookings_count DESC;
            """
        ).fetchall()
        by_user = connection.execute(
            """
            SELECT
                users.name AS user_name,
                COUNT(bookings.id) AS bookings_count
            FROM users
            LEFT JOIN bookings
                ON users.id = bookings.user_id
                AND bookings.is_cancelled = 0
            GROUP BY users.id, users.name
            ORDER BY bookings_count DESC;
            """
        ).fetchall()
        popular = connection.execute(
            """
            SELECT
                rooms.name AS room_name,
                COUNT(bookings.id) AS bookings_count
            FROM rooms
            JOIN bookings
                ON rooms.id = bookings.room_id
            WHERE bookings.is_cancelled = 0
            GROUP BY rooms.id, rooms.name
            HAVING COUNT(bookings.id) > ?
            ORDER BY bookings_count DESC;
            """,
            (1,),
        ).fetchall()
        users = connection.execute(
            """
            SELECT
                id,
                name,
                email
            FROM users
            ORDER BY name;
            """
        ).fetchall()
    context = {
        "bookings_count": bookings_count,
        "summary": summary,
        "statistics": by_room,
        "by_user": by_user,
        "popular": popular,
        "users": users,
    }
    return render(request, "bookings/statistics.html", context)
