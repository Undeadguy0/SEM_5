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
    assert "Статистика" in text
    assert 'class="nav"' in text
    assert 'class="btn btn-primary' in text
    assert 'name="viewport"' in text


def test_room_list_and_detail():
    client = _client()
    listing = client.get("/rooms/")
    listing_text = listing.content.decode()
    assert listing.status_code == 200
    assert "Переговорная «Альфа»" in listing_text
    assert "Найти свободное помещение" in listing_text
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


def test_available_rooms_by_date():
    client = _client()
    form = client.get("/rooms/available/")
    form_text = form.content.decode()
    assert form.status_code == 200
    assert "Свободные помещения" in form_text
    assert 'name="date"' in form_text

    found = client.get("/rooms/available/?date=2026-09-29")
    found_text = found.content.decode()
    assert found.status_code == 200
    assert "Переговорная «Альфа»" not in found_text
    assert "Переговорная «Гамма»" in found_text


def test_statistics_page():
    response = _client().get("/bookings/statistics/")
    text = response.content.decode()
    assert response.status_code == 200
    assert "Статистика бронирований" in text
    assert "Переговорная «Альфа»" in text
    assert "Количество бронирований: 2" in text
    assert "Иванов И.И." in text


@override_settings(DEBUG=False)
def test_unknown_url_uses_custom_404():
    response = _client().get("/no-such-page/")
    text = response.content.decode()
    assert response.status_code == 404
    assert "Страница не найдена" in text


def test_room_search_by_name_and_equipment():
    client = _client()
    by_name = client.get("/rooms/?q=Гамма")
    by_name_text = by_name.content.decode()
    assert by_name.status_code == 200
    assert "Переговорная «Гамма»" in by_name_text
    assert "Переговорная «Альфа»" not in by_name_text

    by_equipment = client.get("/rooms/?q=проектор")
    by_equipment_text = by_equipment.content.decode()
    assert "Переговорная «Альфа»" in by_equipment_text
    assert "Переговорная «Гамма»" in by_equipment_text
    assert "Без названия" not in by_equipment_text


def test_available_rooms_reject_bad_date():
    response = _client().get("/rooms/available/?date=не-дата")
    text = response.content.decode()
    assert response.status_code == 200
    assert "Укажите корректную дату." in text
    assert "Переговорная «Гамма»" not in text


def test_booking_filters_sort_and_search():
    client = _client()
    by_room = client.get("/bookings/?room=1&sort=room")
    by_room_text = by_room.content.decode()
    assert by_room.status_code == 200
    assert "Иванов И.И." in by_room_text

    by_user = client.get("/bookings/?user=1")
    by_user_text = by_user.content.decode()
    assert "Всего: 1" in by_user_text
    assert 'href="/bookings/1/"' in by_user_text
    assert 'href="/bookings/2/"' not in by_user_text

    by_topic = client.get("/bookings/?q=Планёрка")
    by_topic_text = by_topic.content.decode()
    assert "Всего: 1" in by_topic_text
    assert 'href="/bookings/1/"' in by_topic_text
    assert 'href="/bookings/2/"' not in by_topic_text

    bad_date = client.get("/bookings/?date=не-дата")
    assert "Укажите корректную дату." in bad_date.content.decode()

    bad_page = client.get("/bookings/?page=abc")
    assert bad_page.status_code == 200
    assert "Иванов И.И." in bad_page.content.decode()

    bad_sort = client.get("/bookings/?sort=name;drop")
    assert bad_sort.status_code == 200
