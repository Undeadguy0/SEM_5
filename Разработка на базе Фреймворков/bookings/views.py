"""Страницы бронирований."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from domain.bookings import find_booking_by_id
from homepage.catalog import load_catalog
from homepage.views import http_not_found


def bookings(request: HttpRequest) -> HttpResponse:
    """Показать список всех бронирований."""
    _, _, booking_list = load_catalog()
    context = {"bookings": booking_list}
    return render(request, "bookings/booking_list.html", context)


def booking_detail(
    request: HttpRequest,
    booking_id: int,
) -> HttpResponse:
    """Показать карточку одного бронирования."""
    _, _, booking_list = load_catalog()
    booking = find_booking_by_id(booking_list, booking_id)
    if booking is None:
        return http_not_found(
            request,
            "Бронирование не найдено.",
            "bookings:bookings",
            "К списку бронирований",
        )

    context = {"booking": booking}
    return render(request, "bookings/booking_detail.html", context)
