"""Бронирование переговорной."""

from django.db import models

from rooms.models import Room
from users.models import User


class Booking(models.Model):
    """Бронирование помещения пользователем."""

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
    is_cancelled = models.BooleanField(
        default=False,
        verbose_name="Бронирование отменено",
    )

    class Meta:
        """Сортировка и названия модели."""

        ordering = ["booking_date", "pk"]
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"

    def cancel(self) -> None:
        """Отменить бронирование и сохранить только этот признак."""
        self.is_cancelled = True
        self.save(update_fields=["is_cancelled"])

    def __str__(self) -> str:
        """Вернуть помещение, дату и организатора."""
        return f"{self.room} — {self.booking_date} ({self.user})"
