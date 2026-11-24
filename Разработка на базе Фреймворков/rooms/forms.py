"""Форма помещения с загрузкой изображения."""

from django import forms
from django.core.exceptions import ValidationError

from rooms.models import Room


def validate_image_size(image):
    """Отклонить изображение больше 2 МБ.

    Args:
        image: Загруженный файл или пустое значение.

    Raises:
        ValidationError: Если файл превышает лимит.
    """
    size = getattr(image, "size", 0) or 0
    if size > 2 * 1024 * 1024:
        raise ValidationError(
            "Размер изображения не должен превышать 2 МБ.",
        )


class RoomForm(forms.ModelForm):
    """Создание и правка помещения.

    Slug и is_large пользователь не задаёт: адрес собирает модель,
    а признак большого помещения считает база.
    """

    class Meta:
        """Поля, которые можно менять с сайта."""

        model = Room
        fields = ["name", "capacity", "equipment", "image"]
        labels = {
            "name": "Название",
            "capacity": "Вместимость",
            "equipment": "Оборудование",
            "image": "Изображение",
        }
        help_texts = {
            "image": "Необязательно. Файл сохранится в media/rooms/.",
            "capacity": "Число мест. От 50 помещение считается большим.",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "capacity": forms.NumberInput(
                attrs={"class": "form-control", "min": 1},
            ),
            "equipment": forms.Textarea(
                attrs={"class": "form-control", "rows": 3},
            ),
            "image": forms.ClearableFileInput(
                attrs={"class": "form-control"},
            ),
        }

    def __init__(self, *args, **kwargs):
        """Подключить ограничение размера файла."""
        super().__init__(*args, **kwargs)
        self.fields["image"].validators.append(validate_image_size)

    def clean_capacity(self):
        """Запретить вместимость меньше одного места.

        Returns:
            Вместимость, если она положительная.

        Raises:
            ValidationError: Если мест нет.
        """
        capacity = self.cleaned_data["capacity"]
        if capacity < 1:
            raise ValidationError(
                "Вместимость должна быть больше нуля.",
            )
        return capacity
