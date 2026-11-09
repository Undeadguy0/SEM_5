"""Страницы помещений."""

from datetime import date
from datetime import datetime

from django.db.models import Q
from django.http import Http404
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from bookings.models import Booking
from domain.bookings import get_booking_status
from homepage.views import http_not_found
from rooms.models import Room


def _matching_rooms(query: str):
    """Отобрать помещения по названию или оборудованию.

    Args:
        query: Подстрока поиска. Пустая строка оставляет все записи.

    Returns:
        QuerySet помещений.
    """
    rooms = Room.objects.order_by("name")
    if not query:
        return rooms
    return rooms.filter(
        Q(name__icontains=query) | Q(equipment__icontains=query),
    )


def rooms(request: HttpRequest) -> HttpResponse:
    """Показать помещения и отбор по вместимости."""
    query = request.GET.get("q", "").strip()
    room_list = _matching_rooms(query)
    large_rooms = (
        _matching_rooms(query)
        .filter(capacity__gte=8)
        .order_by("capacity")
    )
    context = {
        "rooms": room_list,
        "large_rooms": large_rooms,
        "query": query,
    }
    return render(request, "rooms/room_list.html", context)


def room_detail(request: HttpRequest, room_id: int) -> HttpResponse:
    """Показать карточку помещения и доступность на сегодня."""
    try:
        room = get_object_or_404(Room, pk=room_id)
    except Http404:
        return http_not_found(
            request,
            "Помещение не найдено.",
            "rooms:list",
            "К списку помещений",
        )
    today = date.today()
    occupied = Booking.objects.filter(
        room=room,
        booking_date=today,
        is_cancelled=False,
    ).count()
    available = occupied == 0
    context = {
        "room": room,
        "today": today.isoformat(),
        "available": available,
        "status": get_booking_status(available),
    }
    return render(request, "rooms/room_detail.html", context)


def available_rooms(request: HttpRequest) -> HttpResponse:
    """Найти помещения без активного бронирования на дату."""
    booking_date = request.GET.get("date", "").strip()
    room_list = []
    error = None
    if booking_date:
        try:
            selected_date = datetime.strptime(
                booking_date,
                "%Y-%m-%d",
            ).date()
        except ValueError:
            error = "Укажите корректную дату."
        else:
            booked_room_ids = Booking.objects.filter(
                booking_date=selected_date,
                is_cancelled=False,
            ).values_list("room_id", flat=True)
            room_list = Room.objects.exclude(
                pk__in=booked_room_ids,
            ).order_by("name")
    context = {
        "rooms": room_list,
        "booking_date": booking_date,
        "error": error,
    }
    return render(request, "rooms/available.html", context)
