"""Страницы помещений."""

from contextlib import closing
from datetime import date

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db.database import get_connection
from domain.bookings import get_booking_status
from homepage.views import http_not_found


def rooms(request: HttpRequest) -> HttpResponse:
    """Показать список помещений и отбор по вместимости."""
    with closing(get_connection()) as connection:
        room_list = connection.execute(
            """
            SELECT
                id,
                name,
                capacity,
                equipment
            FROM rooms
            ORDER BY name;
            """
        ).fetchall()
        large_rooms = connection.execute(
            """
            SELECT
                id,
                name,
                capacity,
                equipment
            FROM rooms
            WHERE capacity >= ?
            ORDER BY capacity;
            """,
            (8,),
        ).fetchall()
    context = {
        "rooms": room_list,
        "large_rooms": large_rooms,
    }
    return render(request, "rooms/room_list.html", context)


def room_detail(request: HttpRequest, room_id: int) -> HttpResponse:
    """Показать карточку помещения и доступность на сегодня."""
    with closing(get_connection()) as connection:
        room = connection.execute(
            """
            SELECT
                id,
                name,
                capacity,
                equipment
            FROM rooms
            WHERE id = ?;
            """,
            (room_id,),
        ).fetchone()
        if room is None:
            return http_not_found(
                request,
                "Помещение не найдено.",
                "rooms:list",
                "К списку помещений",
            )
        today = date.today().isoformat()
        occupied = connection.execute(
            """
            SELECT COUNT(*) AS occupied
            FROM bookings
            WHERE room_id = ?
                AND booking_date = ?
                AND is_cancelled = 0;
            """,
            (room_id, today),
        ).fetchone()
    available = occupied["occupied"] == 0
    context = {
        "room": room,
        "today": today,
        "available": available,
        "status": get_booking_status(available),
    }
    return render(request, "rooms/room_detail.html", context)


def available_rooms(request: HttpRequest) -> HttpResponse:
    """Найти помещения без активного бронирования на дату."""
    booking_date = request.GET.get("date") or ""
    room_list = []
    if booking_date:
        with closing(get_connection()) as connection:
            room_list = connection.execute(
                """
                SELECT
                    rooms.id,
                    rooms.name,
                    rooms.capacity,
                    rooms.equipment
                FROM rooms
                WHERE rooms.id NOT IN (
                    SELECT bookings.room_id
                    FROM bookings
                    WHERE bookings.booking_date = ?
                        AND bookings.is_cancelled = 0
                )
                ORDER BY rooms.name;
                """,
                (booking_date,),
            ).fetchall()
    context = {
        "rooms": room_list,
        "booking_date": booking_date,
    }
    return render(request, "rooms/available.html", context)
