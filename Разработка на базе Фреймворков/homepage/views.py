"""Главная страница и ответы 404."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from bookings.models import Booking
from rooms.models import Room


def index(request: HttpRequest) -> HttpResponse:
    """Показать описание проекта и сводку из ORM."""
    context = {
        "rooms_count": Room.objects.count(),
        "bookings_count": Booking.objects.filter(
            is_cancelled=False,
        ).count(),
    }
    return render(request, "homepage/index.html", context)


def page_not_found(
    request: HttpRequest,
    exception: Exception,
) -> HttpResponse:
    """Показать страницу 404 в общем каркасе сайта."""
    return render(
        request,
        "homepage/page_not_found.html",
        status=404,
    )


def http_not_found(
    request: HttpRequest,
    message: str,
    back_url_name: str,
    back_label: str,
) -> HttpResponse:
    """Вернуть каркас сайта со статусом 404.

    Args:
        request: HTTP-запрос.
        message: Пояснение, какой объект не найден.
        back_url_name: Имя маршрута для ссылки возврата.
        back_label: Текст ссылки возврата.

    Returns:
        HTTP-ответ со статусом 404.
    """
    context = {
        "message": message,
        "back_url_name": back_url_name,
        "back_label": back_label,
    }
    return render(
        request,
        "homepage/object_not_found.html",
        context,
        status=404,
    )
