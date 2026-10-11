"""Проверка страниц Django."""

import pytest

pytest.importorskip("django")

from django.test import Client  # noqa: E402
from django.test import override_settings  # noqa: E402


def _client() -> Client:
    return Client(SERVER_NAME="localhost")


def test_index_has_navigation():
    response = _client().get("/")
    text = response.content.decode()
    assert response.status_code == 200
    assert "Система бронирования переговорных" in text
    assert 'class="nav"' in text
    assert 'class="btn btn-primary' in text
    assert 'name="viewport"' in text


def test_room_list_and_detail():
    client = _client()
    listing = client.get("/rooms/")
    listing_text = listing.content.decode()
    assert listing.status_code == 200
    assert "Переговорная «Альфа»" in listing_text
    assert "list-group" in listing_text

    detail = client.get("/rooms/1/")
    detail_text = detail.content.decode()
    assert detail.status_code == 200
    assert "Вместимость: 8 мест." in detail_text
    assert "card-body" in detail_text
    assert (
        "Переговорная свободна" in detail_text
        or "Переговорная уже занята" in detail_text
    )

    missing = client.get("/rooms/999/")
    assert missing.status_code == 404
    assert "Помещение не найдено." in missing.content.decode()


def test_booking_list_and_detail():
    client = _client()
    listing = client.get("/bookings/")
    listing_text = listing.content.decode()
    assert listing.status_code == 200
    assert "Иванов И.И." in listing_text
    assert "bg-success" in listing_text

    detail = client.get("/bookings/1/")
    detail_text = detail.content.decode()
    assert detail.status_code == 200
    assert "Планёрка отдела разработки" in detail_text
    assert "ivanov@example.com" in detail_text
    assert "Активно" in detail_text

    missing = client.get("/bookings/999/")
    assert missing.status_code == 404
    assert "Бронирование не найдено." in missing.content.decode()


@override_settings(DEBUG=False)
def test_unknown_url_uses_custom_404():
    response = _client().get("/no-such-page/")
    text = response.content.decode()
    assert response.status_code == 404
    assert "Страница не найдена" in text
    assert "bootstrap@5.3.3" in text
