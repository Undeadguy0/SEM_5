"""Страницы бронирований."""

from html import escape

from django.http import HttpRequest, HttpResponse
from django.urls import reverse

from domain.bookings import find_booking_by_id
from homepage.catalog import load_catalog
from homepage.views import http_not_found, page
from models import Booking


def bookings(request: HttpRequest) -> HttpResponse:
    """Показать список всех бронирований."""
    _, _, booking_list = load_catalog()
    if not booking_list:
        items = '<p class="lead">Бронирований пока нет.</p>'
    else:
        rows = []
        for booking in booking_list:
            url = reverse("booking_detail", args=[booking.id])
            rows.append(
                '<a class="list-group-item list-group-item-action" '
                f'href="{url}">'
                f"<strong>#{booking.id} {escape(booking.room.name)}</strong> "
                f"{escape(booking.booking_date)} "
                f"{escape(booking.start_time)}–{escape(booking.end_time)} "
                f"{escape(booking.user.name)} "
                f"{_status_badge(booking)}"
                "</a>"
            )
        items = '<div class="list-group">' + "".join(rows) + "</div>"
    content = (
        '<h1 class="display-4">Бронирования</h1>'
        '<p class="lead">Все записи, включая отменённые.</p>'
        f"{items}"
    )
    return HttpResponse(page("Бронирования", content))


def booking_detail(
    request: HttpRequest,
    booking_id: int,
) -> HttpResponse:
    """Показать карточку одного бронирования."""
    _, _, booking_list = load_catalog()
    booking = find_booking_by_id(booking_list, booking_id)
    if booking is None:
        return http_not_found(
            "Бронирование не найдено.",
            reverse("bookings"),
            "К списку бронирований",
        )

    room_url = reverse("room_detail", args=[booking.room.id])
    content = (
        '<div class="card">'
        '<div class="card-body">'
        f'<h1 class="display-4">Бронирование #{booking.id}</h1>'
        f'<p class="lead">{escape(booking.topic)}</p>'
        '<ul class="list-group list-group-flush mb-3">'
        '<li class="list-group-item">Помещение: '
        f'<a href="{room_url}">{escape(booking.room.name)}</a></li>'
        '<li class="list-group-item">Организатор: '
        f"{escape(booking.user.name)}, "
        f"{escape(booking.user.email)}</li>"
        '<li class="list-group-item">Дата: '
        f"{escape(booking.booking_date)}</li>"
        '<li class="list-group-item">Время: '
        f"{escape(booking.start_time)}–"
        f"{escape(booking.end_time)}</li>"
        '<li class="list-group-item">Статус: '
        f"{_status_badge(booking)}</li>"
        "</ul>"
        f'<a class="btn btn-primary" href="{reverse("bookings")}">'
        "К списку бронирований</a>"
        "</div>"
        "</div>"
    )
    return HttpResponse(page(f"Бронирование #{booking.id}", content))


def _status_badge(booking: Booking) -> str:
    """Вернуть значок статуса бронирования."""
    if booking.is_cancelled:
        label = "Отменено"
        style = "bg-secondary"
    else:
        label = "Активно"
        style = "bg-success"
    return f'<span class="badge {style}">{label}</span>'
