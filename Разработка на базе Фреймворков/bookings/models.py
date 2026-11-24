"""Бронирование переговорной."""

from django.db import models

from rooms.models import Room
from users.models import User


class BookingQuerySet(models.QuerySet):
    """Набор запросов для работы с бронированиями."""

    def active(self):
        """Вернуть только активные бронирования."""
        return self.filter(status=self.model.Status.ACTIVE)

    def cancelled(self):
        """Вернуть только отменённые бронирования."""
        return self.filter(status=self.model.Status.CANCELLED)

    def completed(self):
        """Вернуть только завершённые бронирования."""
        return self.filter(status=self.model.Status.COMPLETED)

    def for_date(self, selected_date):
        """Вернуть бронирования на указанную дату.

        Args:
            selected_date: Дата поля booking_date.
        """
        return self.filter(booking_date=selected_date)


class BookingManager(models.Manager.from_queryset(BookingQuerySet)):
    """Менеджер модели Booking с методами QuerySet."""


class Booking(models.Model):
    """Бронирование помещения пользователем."""

    class Status(models.TextChoices):
        """Состояние бронирования."""

        ACTIVE = "active", "Активно"
        CANCELLED = "cancelled", "Отменено"
        COMPLETED = "completed", "Завершено"

    objects = BookingManager()

    room = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        related_name="bookings",
        verbose_name="Помещение",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="bookings",
        verbose_name="Пользователь",
    )
    booking_date = models.DateField(
        verbose_name="Дата бронирования",
    )
    start_time = models.CharField(
        max_length=5,
        verbose_name="Время начала",
    )
    end_time = models.CharField(
        max_length=5,
        verbose_name="Время окончания",
    )
    topic = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Тема",
    )
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name="Статус бронирования",
    )

    class Meta:
        """Сортировка и названия модели."""

        ordering = ["booking_date", "pk"]
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"

    def cancel(self) -> None:
        """Отменить бронирование, не удаляя запись."""
        self.status = self.Status.CANCELLED
        self.save(update_fields=["status"])

    def __str__(self) -> str:
        """Вернуть помещение, дату и организатора."""
        return f"{self.room} — {self.booking_date} ({self.user})"
