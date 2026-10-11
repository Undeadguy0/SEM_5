"""Страницы помещений."""

from datetime import date
from html import escape

from django.http import HttpRequest, HttpResponse
from django.urls import reverse

from domain.bookings import get_booking_status, is_room_available
from domain.rooms import find_room_by_id
from homepage.catalog import load_catalog
from homepage.views import http_not_found, page


def rooms(request: HttpRequest) -> HttpResponse:
    """Показать список всех помещений."""
    room_list, _, _ = load_catalog()
    if not room_list:
        items = '<p class="lead">Помещений пока нет.</p>'
    else:
        rows = []
        for room in room_list:
            url = reverse("room_detail", args=[room.id])
            equipment = _equipment(room.equipment)
            rows.append(
                '<a class="list-group-item list-group-item-action" '
                f'href="{url}">'
                f"<strong>{escape(room.name)}</strong> "
                '<span class="badge bg-secondary">'
                f"{room.capacity} мест</span>"
                f'<div class="text-body-secondary">{equipment}</div>'
                "</a>"
            )
        items = '<div class="list-group">' + "".join(rows) + "</div>"
    content = (
        '<h1 class="display-4">Помещения</h1>'
        '<p class="lead">Все переговорные комнаты офиса.</p>'
        f"{items}"
    )
    return HttpResponse(page("Помещения", content))


def room_detail(request: HttpRequest, room_id: int) -> HttpResponse:
    """Показать карточку помещения и доступность на сегодня."""
    room_list, _, booking_list = load_catalog()
    room = find_room_by_id(room_list, room_id)
    if room is None:
        return http_not_found(
            "Помещение не найдено.",
            reverse("rooms"),
            "К списку помещений",
        )

    today = date.today().isoformat()
    available = is_room_available(booking_list, room.id, today)
    status = get_booking_status(available)
    if available:
        badge = "bg-success"
    else:
        badge = "bg-danger"
    content = (
        '<div class="card">'
        '<div class="card-body">'
        f'<h1 class="display-4">{escape(room.name)}</h1>'
        f'<p class="lead">Вместимость: {room.capacity} мест.</p>'
        '<ul class="list-group list-group-flush mb-3">'
        '<li class="list-group-item">Оборудование: '
        f"{_equipment(room.equipment)}</li>"
        '<li class="list-group-item">На сегодня '
        f"({escape(today)}): "
        f'<span class="badge {badge}">{escape(status)}</span></li>'
        "</ul>"
        f'<a class="btn btn-primary" href="{reverse("rooms")}">'
        "К списку помещений</a>"
        "</div>"
        "</div>"
    )
    return HttpResponse(page(room.name, content))


def _equipment(equipment: list[str]) -> str:
    """Собрать экранированный список оборудования."""
    if not equipment:
        return "нет"
    return ", ".join(escape(item) for item in equipment)
