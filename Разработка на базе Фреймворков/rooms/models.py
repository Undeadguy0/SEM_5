"""Помещение Roomly."""

from django.db import models
from django.db.models import Case
from django.db.models import Value
from django.db.models import When
from django.urls import reverse
from django.utils.text import slugify
from unidecode import unidecode


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
    is_large = models.GeneratedField(
        expression=Case(
            When(capacity__gte=50, then=Value(True)),
            default=Value(False),
            output_field=models.BooleanField(),
        ),
        output_field=models.BooleanField(),
        db_persist=True,
        verbose_name="Большое помещение",
    )
    equipment = models.TextField(
        blank=True,
        default="",
        verbose_name="Оборудование",
    )
    slug = models.SlugField(
        max_length=180,
        unique=True,
        editable=False,
        verbose_name="URL-идентификатор",
    )

    class Meta:
        """Сортировка и названия модели."""

        ordering = ["name"]
        verbose_name = "Помещение"
        verbose_name_plural = "Помещения"

    def save(self, *args, **kwargs):
        """Заполнить slug из названия и первичного ключа."""
        if not self.slug:
            transliterated_name = unidecode(self.name or "")
            base_slug = slugify(transliterated_name) or "room"
            if self.pk:
                self.slug = f"{base_slug}-{self.pk}"
            else:
                super().save(*args, **kwargs)
                self.slug = f"{base_slug}-{self.pk}"
                super().save(update_fields=["slug"])
                return
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Вернуть адрес подробной страницы помещения."""
        return reverse(
            "rooms:detail",
            kwargs={"slug": self.slug},
        )

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
