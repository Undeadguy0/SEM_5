"""Вспомогательные функции ввода."""

from datetime import datetime


def input_int(prompt: str) -> int:
    """Запросить у пользователя целое число.

    Args:
        prompt: Текст приглашения к вводу.

    Returns:
        Введенное целое число.
    """
    while True:
        try:
            value = int(input(prompt).strip())
            return value
        except ValueError:
            print("Ошибка: введите целое число.")


def input_date(prompt: str) -> str:
    """Запросить дату в формате DD.MM.YYYY.

    Args:
        prompt: Текст приглашения к вводу.

    Returns:
        Дата в формате YYYY-MM-DD.
    """
    while True:
        try:
            value = input(prompt).strip()
            dt = datetime.strptime(value, "%d.%m.%Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            print("Ошибка: введите дату в формате DD.MM.YYYY " "(например, 29.09.2026).")


def input_time(prompt: str) -> str:
    """Запросить время в формате HH:MM.

    Args:
        prompt: Текст приглашения к вводу.

    Returns:
        Время в формате HH:MM.
    """
    while True:
        try:
            value = input(prompt).strip()
            datetime.strptime(value, "%H:%M")
            return value
        except ValueError:
            print("Ошибка: введите время в формате HH:MM " "(например, 10:00).")
