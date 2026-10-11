"""Главная страница и общий HTML-каркас."""

from html import escape

from django.http import HttpRequest, HttpResponse
from django.urls import reverse

BOOTSTRAP = (
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/"
    "dist/css/bootstrap.min.css"
)


def page(title: str, content: str) -> str:
    """Собрать HTML-страницу с навигацией и Bootstrap 5.3.

    Args:
        title: Заголовок вкладки браузера.
        content: HTML основной области.

    Returns:
        Полный HTML-документ.
    """
    home = reverse("index")
    rooms_url = reverse("rooms")
    bookings_url = reverse("bookings")
    return (
        "<!DOCTYPE html>"
        '<html lang="ru">'
        "<head>"
        '<meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, '
        'initial-scale=1">'
        f"<title>{escape(title)}</title>"
        f'<link rel="stylesheet" href="{BOOTSTRAP}">'
        "</head>"
        "<body>"
        '<nav class="navbar navbar-expand-lg bg-light '
        'border-bottom mb-4">'
        '<div class="container">'
        f'<a class="navbar-brand" href="{home}">Roomly</a>'
        '<div class="nav">'
        f'<a class="nav-link" href="{home}">Главная</a>'
        f'<a class="nav-link" href="{rooms_url}">Помещения</a>'
        f'<a class="nav-link" href="{bookings_url}">'
        "Бронирования</a>"
        "</div>"
        "</div>"
        "</nav>"
        f'<main class="container pb-5">{content}</main>'
        "</body>"
        "</html>"
    )


def index(request: HttpRequest) -> HttpResponse:
    """Показать описание проекта и ссылки на разделы."""
    rooms_url = reverse("rooms")
    bookings_url = reverse("bookings")
    content = (
        '<h1 class="display-4">Система бронирования переговорных</h1>'
        '<p class="lead">Веб-интерфейс показывает помещения и '
        "бронирования из JSON-файлов консольного приложения.</p>"
        "<p>Создание и отмена бронирований пока выполняются "
        "в консольной программе <code>python main.py</code>.</p>"
        '<p class="mt-4">'
        f'<a class="btn btn-primary me-2" href="{rooms_url}">'
        "Список помещений</a>"
        f'<a class="btn btn-primary" href="{bookings_url}">'
        "Список бронирований</a>"
        "</p>"
    )
    return HttpResponse(page("Главная", content))


def page_not_found(
    request: HttpRequest,
    exception: Exception,
) -> HttpResponse:
    """Показать страницу 404 в общем каркасе сайта."""
    content = (
        '<h1 class="display-4">Страница не найдена</h1>'
        '<p class="lead">Запрошенный адрес не существует.</p>'
        f'<a class="btn btn-primary" href="{reverse("index")}">'
        "На главную</a>"
    )
    return HttpResponse(page("Не найдено", content), status=404)


def http_not_found(
    message: str,
    back_url: str,
    back_label: str,
) -> HttpResponse:
    """Вернуть каркас сайта со статусом 404.

    Args:
        message: Пояснение, какой объект не найден.
        back_url: Адрес ссылки возврата.
        back_label: Текст ссылки возврата.

    Returns:
        HTTP-ответ со статусом 404.
    """
    content = (
        '<h1 class="display-4">Не найдено</h1>'
        f'<p class="lead">{escape(message)}</p>'
        f'<a class="btn btn-primary" href="{back_url}">'
        f"{escape(back_label)}</a>"
    )
    return HttpResponse(page("Не найдено", content), status=404)
