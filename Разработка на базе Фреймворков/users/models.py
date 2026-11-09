"""Пользователь предметной области Roomly."""

from django.db import models


class User(models.Model):
    """Организатор бронирования.

    Это не встроенная модель аутентификации Django.
    """

    name = models.CharField(
        max_length=200,
        verbose_name="Имя пользователя",
    )
    email = models.EmailField(
        verbose_name="Электронная почта",
    )

    class Meta:
        """Сортировка и названия модели."""

        ordering = ["name"]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self) -> str:
        """Вернуть имя пользователя."""
        return self.name
