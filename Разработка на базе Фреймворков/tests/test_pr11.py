"""Формы бронирования и загрузка изображения помещения."""

from datetime import timedelta
from io import BytesIO
from pathlib import Path

import pytest

pytest.importorskip("django")
pytest.importorskip("PIL")

from django.core.files.uploadedfile import SimpleUploadedFile  # noqa: E402
from django.db import transaction  # noqa: E402
from django.test import Client  # noqa: E402
from django.utils import timezone  # noqa: E402
from PIL import Image  # noqa: E402

from bookings.models import Booking  # noqa: E402
from django.conf import settings  # noqa: E402
from rooms.models import Room  # noqa: E402
from users.models import User  # noqa: E402


def _client(**kwargs) -> Client:
    return Client(SERVER_NAME="localhost", **kwargs)


def _png(name: str = "room.png") -> SimpleUploadedFile:
    buffer = BytesIO()
    Image.new("RGB", (8, 8), "red").save(buffer, format="PNG")
    return SimpleUploadedFile(
        name,
        buffer.getvalue(),
        content_type="image/png",
    )


@pytest.fixture
def db_rollback():
    """Откатить записи и убрать файлы, созданные тестом."""
    root = Path(settings.MEDIA_ROOT) / "rooms"
    before = set(root.glob("*")) if root.exists() else set()
    with transaction.atomic():
        yield
        transaction.set_rollback(True)
    if root.exists():
        for path in root.glob("*"):
            if path not in before and path.is_file():
                path.unlink()


def _booking_data(room_id, user_id, selected, topic):
    return {
        "room": room_id,
        "user": user_id,
        "booking_date": selected.isoformat(),
        "start_time": "10:00",
        "end_time": "11:00",
        "topic": topic,
    }


def test_filter_form_keeps_values_and_rejects_bad_date(db_rollback):
    """Форма фильтрации проверяет GET и не падает на мусоре."""
    client = _client()
    page = client.get("/bookings/?date=2026-09-29&room=1&sort=room")
    text = page.content.decode()
    assert page.status_code == 200
    assert 'value="2026-09-29"' in text
    assert "Применить фильтры" in text
    assert "csrfmiddlewaretoken" in text

    bad_room = client.get("/bookings/?room=99999")
    assert bad_room.status_code == 200
    assert "Проверьте корректность параметров фильтрации." in (
        bad_room.content.decode()
    )
    assert "Иванов И.И." in bad_room.content.decode()


def test_create_edit_and_cancel_booking(db_rollback):
    """Создание, конфликт, правка и отмена идут через формы."""
    client = _client()
    today = timezone.localdate()
    tomorrow = today + timedelta(days=1)
    later = today + timedelta(days=2)
    room = Room.objects.get(pk=3)
    other = Room.objects.get(pk=1)
    user = User.objects.get(pk=1)
    before = Booking.objects.count()

    past = client.post(
        "/bookings/create/",
        _booking_data(room.pk, user.pk, today - timedelta(days=1), "Прошлое"),
    )
    past_text = past.content.decode()
    assert past.status_code == 200
    assert "Нельзя создать бронирование на прошедшую дату." in past_text
    assert Booking.objects.filter(topic="Прошлое").count() == 0

    turned = client.post(
        "/bookings/create/",
        {
            **_booking_data(room.pk, user.pk, tomorrow, "Интервал"),
            "end_time": "09:00",
        },
    )
    assert turned.status_code == 200
    assert "позже времени начала" in turned.content.decode()

    created = client.post(
        "/bookings/create/",
        _booking_data(room.pk, user.pk, tomorrow, "Новая планёрка"),
    )
    assert created.status_code == 302
    booking = Booking.objects.get(topic="Новая планёрка")
    assert booking.status == Booking.Status.ACTIVE
    assert booking.booking_date == tomorrow
    assert Booking.objects.count() == before + 1

    conflict = client.post(
        "/bookings/create/",
        _booking_data(room.pk, user.pk, tomorrow, "Повтор"),
    )
    assert conflict.status_code == 200
    assert "уже забронировано" in conflict.content.decode()
    assert Booking.objects.filter(topic="Повтор").count() == 0

    same = client.post(
        f"/bookings/{booking.pk}/edit/",
        _booking_data(room.pk, user.pk, tomorrow, "Новая планёрка"),
    )
    assert same.status_code == 302
    assert Booking.objects.filter(topic="Новая планёрка").count() == 1

    other_booking = Booking.objects.create(
        room=other,
        user=user,
        booking_date=later,
        start_time="12:00",
        end_time="13:00",
        topic="Вторая",
    )
    clash = client.post(
        f"/bookings/{other_booking.pk}/edit/",
        _booking_data(room.pk, user.pk, tomorrow, "Вторая"),
    )
    assert clash.status_code == 200
    assert "уже забронировано" in clash.content.decode()
    other_booking.refresh_from_db()
    assert other_booking.room_id == other.pk
    assert other_booking.booking_date == later

    missing = client.get("/bookings/999/edit/")
    assert missing.status_code == 404
    assert "Бронирование не найдено." in missing.content.decode()

    opened = client.get(f"/bookings/{booking.pk}/cancel/")
    assert opened.status_code == 405
    cancelled = client.post(f"/bookings/{booking.pk}/cancel/")
    assert cancelled.status_code == 302
    booking.refresh_from_db()
    assert booking.status == Booking.Status.CANCELLED
    again = client.post(f"/bookings/{booking.pk}/cancel/")
    assert again.status_code == 404

    replacement = client.post(
        "/bookings/create/",
        _booking_data(room.pk, user.pk, tomorrow, "После отмены"),
    )
    assert replacement.status_code == 302
    assert Booking.objects.filter(topic="После отмены").count() == 1


def test_room_image_upload(db_rollback):
    """Картинка сохраняется в media и видна на карточке."""
    client = _client()
    created = client.post(
        "/rooms/create/",
        {
            "name": "Кабинет с фото",
            "capacity": 6,
            "equipment": "доска",
            "image": _png(),
        },
    )
    assert created.status_code == 302
    room = Room.objects.get(name="Кабинет с фото")
    assert room.image.name.startswith("rooms/")
    assert Path(room.image.path).is_file()
    detail = client.get(room.get_absolute_url())
    detail_text = detail.content.decode()
    assert detail.status_code == 200
    assert room.image.url in detail_text
    assert "Изображение не загружено." not in detail_text

    rejected = client.post(
        "/rooms/create/",
        {
            "name": "Без картинки",
            "capacity": 0,
            "equipment": "",
            "image": SimpleUploadedFile(
                "note.txt",
                b"not an image",
                content_type="text/plain",
            ),
        },
    )
    assert rejected.status_code == 200
    rejected_text = rejected.content.decode()
    assert "изображение" in rejected_text.lower()
    assert "больше нуля" in rejected_text
    assert Room.objects.filter(name="Без картинки").count() == 0

    empty = Room.objects.get(pk=2)
    page = client.get(empty.get_absolute_url())
    assert "Изображение не загружено." in page.content.decode()


def test_create_form_requires_csrf_token(db_rollback):
    """POST без токена не создаёт бронь."""
    client = _client(enforce_csrf_checks=True)
    page = client.get("/bookings/create/")
    assert page.status_code == 200
    assert "csrfmiddlewaretoken" in page.content.decode()
    assert 'value="' in page.content.decode()
    today = timezone.localdate()
    blocked = client.post(
        "/bookings/create/",
        _booking_data(1, 1, today, "Без токена"),
    )
    assert blocked.status_code == 403
    assert Booking.objects.filter(topic="Без токена").count() == 0
