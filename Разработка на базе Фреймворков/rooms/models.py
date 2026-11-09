"""Помещение Roomly."""

from django.db import models


class Room(models.Model):
    """Переговорная комната."""

    name = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Название помещения",
    )
    capacity = models.PositiveIntegerField(
        verbose_name="Вместимость",
    )
    equipment = models.TextField(
        blank=True,
        default="",
        verbose_name="Оборудование",
    )

    class Meta:
        """Сортировка и названия модели."""

        ordering = ["name"]
        verbose_name = "Помещение"
        verbose_name_plural = "Помещения"

    def is_suitable_for(self, people_count: int) -> bool:
        """Проверить, хватает ли мест.

        Args:
            people_count: Число участников.

        Returns:
            True, если вместимость не меньше people_count.
        """
        return self.capacity >= people_count

    def __str__(self) -> str:
        """Вернуть название или заглушку."""
        if self.name:
            return self.name
        return "Без названия"
