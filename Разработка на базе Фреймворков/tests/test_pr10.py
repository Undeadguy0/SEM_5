"""Проверка статусов, slug и вычисляемого поля ПР10."""

from datetime import date

import pytest

pytest.importorskip("django")

from django.db import transaction  # noqa: E402
from django.test import Client  # noqa: E402
from django.utils.text import slugify  # noqa: E402
from unidecode import unidecode  # noqa: E402

from bookings.models import Booking  # noqa: E402
from rooms.models import Room  # noqa: E402
from users.models import User  # noqa: E402


def _client() -> Client:
    return Client(SERVER_NAME="localhost")


def test_status_slug_and_generated_field():
    """Статусы, адрес помещения и is_large не портят рабочую базу."""
    selected = date(2026, 10, 25)
    with transaction.atomic():
        large = Room.objects.create(
            name="Аудитория 301",
            capacity=60,
        )
        small = Room.objects.create(name="Кабинет", capacity=8)
        organizer = User.objects.create(
            name="Проверка ПР10",
            email="pr10@example.com",
        )
        active = Booking.objects.create(
            room=large,
            user=organizer,
            booking_date=selected,
            start_time="10:00",
            end_time="11:00",
            topic="Активная",
            status=Booking.Status.ACTIVE,
        )
        cancelled = Booking.objects.create(
            room=small,
            user=organizer,
            booking_date=selected,
            start_time="12:00",
            end_time="13:00",
            topic="Отмена",
            status=Booking.Status.CANCELLED,
        )
        completed = Booking.objects.create(
            room=small,
            user=organizer,
            booking_date=selected,
            start_time="14:00",
            end_time="15:00",
            topic="Итоги",
            status=Booking.Status.COMPLETED,
        )
        try:
            assert set(
                Booking.objects.active().filter(
                    user=organizer,
                ),
            ) == {active}
            assert set(
                Booking.objects.cancelled().filter(
                    user=organizer,
                ),
            ) == {cancelled}
            assert set(
                Booking.objects.completed().filter(
                    user=organizer,
                ),
            ) == {completed}
            assert (
                Booking.objects.active()
                .for_date(selected)
                .filter(room=large)
                .count()
                == 1
            )

            found = _client().get(
                "/rooms/available/?date=2026-10-25",
            )
            text = found.content.decode()
            assert found.status_code == 200
            assert "Аудитория 301" not in text
            assert "Кабинет" in text

            large.refresh_from_db()
            small.refresh_from_db()
            base_slug = slugify(unidecode(large.name)) or "room"
            assert large.slug == f"{base_slug}-{large.pk}"
            assert large.get_absolute_url() == (
                f"/rooms/{large.slug}/"
            )
            assert large.is_large is True
            assert small.is_large is False

            page = _client().get(large.get_absolute_url())
            page_text = page.content.decode()
            assert page.status_code == 200
            assert "Большое помещение:" in page_text
            assert ">да<" in page_text or "да." in page_text

            rooms_page = _client().get("/rooms/")
            assert (
                f"Помещения ({Room.objects.count()})"
                in rooms_page.content.decode()
            )

            small.capacity = 50
            small.save()
            small.refresh_from_db()
            assert small.is_large is True

            active.cancel()
            active.refresh_from_db()
            assert active.status == Booking.Status.CANCELLED
            assert Booking.objects.filter(pk=active.pk).exists()
            assert (
                Booking.objects.active()
                .filter(pk=active.pk)
                .exists()
                is False
            )
        finally:
            transaction.set_rollback(True)
