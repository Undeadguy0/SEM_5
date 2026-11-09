"""Главная страница и ответы 404."""

from contextlib import closing

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db.database import get_connection


def index(request: HttpRequest) -> HttpResponse:
    """Показать описание проекта и сводку из SQLite."""
    with closing(get_connection()) as connection:
        rooms_count = connection.execute(
            "SELECT COUNT(*) AS rooms_count FROM rooms;"
        ).fetchone()["rooms_count"]
        bookings_count = connection.execute(
            """
            SELECT COUNT(*) AS bookings_count
            FROM bookings
            WHERE is_cancelled = 0;
            """
        ).fetchone()["bookings_count"]
    context = {
        "rooms_count": rooms_count,
        "bookings_count": bookings_count,
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
