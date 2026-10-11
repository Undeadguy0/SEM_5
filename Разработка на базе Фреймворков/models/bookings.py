"""Класс бронирования."""

from models.rooms import Room
from models.users import User


class Booking:
    """Бронирование переговорной на конкретную дату."""

    def __init__(
        self,
        booking_id: int,
        room: Room,
        user: User,
        booking_date: str,
        start_time: str,
        end_time: str,
        topic: str,
        is_cancelled: bool = False,
    ) -> None:
        """Создать бронирование.

        Args:
            booking_id: Идентификатор бронирования.
            room: Переговорная.
            user: Организатор.
            booking_date: Дата в формате YYYY-MM-DD.
            start_time: Время начала, HH:MM.
            end_time: Время окончания, HH:MM.
            topic: Тема встречи.
            is_cancelled: Признак отмены.
        """
        self.id = booking_id
        self.room = room
        self.user = user
        self.booking_date = booking_date
        self.start_time = start_time
        self.end_time = end_time
        self.topic = topic
        self.is_cancelled = is_cancelled

    def cancel(self) -> None:
        """Отменить бронирование, не удаляя объект."""
        self.is_cancelled = True

    def is_active(self) -> bool:
        """Проверить, что бронирование не отменено.

        Returns:
            True, если бронирование активно.
        """
        return not self.is_cancelled

    def to_dict(self) -> dict:
        """Преобразовать бронирование в словарь для JSON.

        Returns:
            Словарь со ссылками на комнату и пользователя по id.
        """
        return {
            "id": self.id,
            "room_id": self.room.id,
            "user_id": self.user.id,
            "booking_date": self.booking_date,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "topic": self.topic,
            "is_cancelled": self.is_cancelled,
        }

    def __str__(self) -> str:
        """Вернуть описание бронирования с учётом статуса."""
        if self.is_cancelled:
            status = "отменено"
        else:
            status = "активно"
        return (
            f"#{self.id} {self.room.name}, {self.booking_date} "
            f"{self.start_time}-{self.end_time}, {self.user.name}, "
            f"{self.topic} ({status})"
        )
