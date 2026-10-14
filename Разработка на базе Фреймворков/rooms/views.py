"""Страницы помещений."""

from datetime import date

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from domain.bookings import get_booking_status, is_room_available
from domain.rooms import find_room_by_id
from homepage.catalog import load_catalog
from homepage.views import http_not_found


def rooms(request: HttpRequest) -> HttpResponse:
    """Показать список всех помещений."""
    room_list, _, _ = load_catalog()
    context = {"rooms": room_list}
    return render(request, "rooms/room_list.html", context)


def room_detail(request: HttpRequest, room_id: int) -> HttpResponse:
    """Показать карточку помещения и доступность на сегодня."""
    room_list, _, booking_list = load_catalog()
    room = find_room_by_id(room_list, room_id)
    if room is None:
        return http_not_found(
            request,
            "Помещение не найдено.",
            "rooms:list",
            "К списку помещений",
        )

    today = date.today().isoformat()
    available = is_room_available(booking_list, room.id, today)
    context = {
        "room": room,
        "today": today,
        "available": available,
        "status": get_booking_status(available),
    }
    return render(request, "rooms/room_detail.html", context)
