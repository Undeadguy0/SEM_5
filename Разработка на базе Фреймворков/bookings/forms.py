"""Формы списка и карточки бронирования."""

import re

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from bookings.models import Booking
from rooms.models import Room
from users.models import User


_CLOCK_RE = re.compile(r"^(\d{2}):(\d{2})(?::\d{2})?$")


def validate_clock_time(value):
    """Проверить, что строка задаёт время ЧЧ:ММ.

    Args:
        value: Значение поля времени.

    Raises:
        ValidationError: Если часы или минуты не распознаны.
    """
    match = _CLOCK_RE.fullmatch(str(value).strip())
    if match is None:
        raise ValidationError("Укажите время в формате ЧЧ:ММ.")
    hour = int(match.group(1))
    minute = int(match.group(2))
    if hour > 23 or minute > 59:
        raise ValidationError("Укажите время в формате ЧЧ:ММ.")


def normalize_clock_time(value):
    """Привести время к ЧЧ:ММ.

    Args:
        value: Строка, уже проверенная validate_clock_time.

    Returns:
        Время без секунд.
    """
    match = _CLOCK_RE.fullmatch(str(value).strip())
    return f"{int(match.group(1)):02d}:{int(match.group(2)):02d}"


class BookingFilterForm(forms.Form):
    """Параметры фильтрации списка. Запись в базу не создаёт."""

    date = forms.DateField(
        required=False,
        label="Дата бронирования",
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={"type": "date", "class": "form-control"},
        ),
        error_messages={"invalid": "Укажите корректную дату."},
    )
    room = forms.ModelChoiceField(
        queryset=Room.objects.order_by("name"),
        required=False,
        label="Помещение",
        empty_label="Все помещения",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    user = forms.ModelChoiceField(
        queryset=User.objects.order_by("name"),
        required=False,
        label="Пользователь",
        empty_label="Все пользователи",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    status = forms.ChoiceField(
        required=False,
        label="Статус",
        initial="active",
        choices=[
            ("active", "Активные"),
            ("cancelled", "Отменённые"),
            ("completed", "Завершённые"),
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    sort = forms.ChoiceField(
        required=False,
        label="Сортировка",
        initial="date",
        choices=[
            ("date", "По дате"),
            ("room", "По помещению"),
            ("user", "По пользователю"),
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    q = forms.CharField(
        required=False,
        label="Тема",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )


class BookingForm(forms.ModelForm):
    """Создание и редактирование бронирования.

    Поле status в форму не входит: новая запись получает статус
    модели по умолчанию, а при правке статус остаётся у объекта.
    """

    class Meta:
        """Поля, подписи и виджеты формы."""

        model = Booking
        fields = [
            "room",
            "booking_date",
            "start_time",
            "end_time",
            "user",
            "topic",
        ]
        labels = {
            "room": "Помещение",
            "booking_date": "Дата бронирования",
            "start_time": "Время начала",
            "end_time": "Время окончания",
            "user": "Пользователь",
            "topic": "Тема",
        }
        help_texts = {
            "room": "Выберите помещение для бронирования.",
            "booking_date": "Укажите дату проведения мероприятия.",
            "start_time": "Время в формате ЧЧ:ММ.",
            "end_time": "Должно быть позже времени начала.",
        }
        widgets = {
            "room": forms.Select(attrs={"class": "form-select"}),
            "user": forms.Select(attrs={"class": "form-select"}),
            "booking_date": forms.DateInput(
                format="%Y-%m-%d",
                attrs={"type": "date", "class": "form-control"},
            ),
            "start_time": forms.TextInput(
                attrs={"type": "time", "class": "form-control"},
            ),
            "end_time": forms.TextInput(
                attrs={"type": "time", "class": "form-control"},
            ),
            "topic": forms.TextInput(
                attrs={"class": "form-control"},
            ),
        }

    def __init__(self, *args, **kwargs):
        """Подключить проверку формата времени."""
        super().__init__(*args, **kwargs)
        self.fields["start_time"].validators.append(validate_clock_time)
        self.fields["end_time"].validators.append(validate_clock_time)

    def clean_booking_date(self):
        """Запретить новую бронь на прошедшую дату.

        Returns:
            Дата, если она не раньше сегодняшнего дня.

        Raises:
            ValidationError: Если дата уже прошла.
        """
        booking_date = self.cleaned_data["booking_date"]
        if booking_date < timezone.localdate():
            raise ValidationError(
                "Нельзя создать бронирование на прошедшую дату.",
            )
        return booking_date

    def clean_start_time(self):
        """Нормализовать время начала.

        Returns:
            Строка ЧЧ:ММ.
        """
        return normalize_clock_time(self.cleaned_data["start_time"])

    def clean_end_time(self):
        """Нормализовать время окончания.

        Returns:
            Строка ЧЧ:ММ.
        """
        return normalize_clock_time(self.cleaned_data["end_time"])

    def clean(self):
        """Проверить, что интервал времени не перевёрнут.

        Returns:
            Словарь проверенных значений.
        """
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        if start_time and end_time and start_time >= end_time:
            self.add_error(
                "end_time",
                "Время окончания должно быть позже времени начала.",
            )
        return cleaned_data
