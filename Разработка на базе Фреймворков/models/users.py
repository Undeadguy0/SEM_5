"""Класс пользователя."""


class User:
    """Сотрудник, который бронирует переговорную."""

    def __init__(self, user_id: int, name: str, email: str) -> None:
        """Создать пользователя.

        Args:
            user_id: Идентификатор.
            name: Имя организатора.
            email: Электронная почта.
        """
        self.id = user_id
        self.name = name
        self.email = email

    @classmethod
    def from_data(cls, data: dict) -> "User":
        """Создать пользователя из словаря JSON.

        Args:
            data: Словарь с ключами id, name и email.

        Returns:
            Объект User.
        """
        return cls(
            user_id=int(data["id"]),
            name=str(data["name"]),
            email=str(data["email"]),
        )

    def to_dict(self) -> dict:
        """Преобразовать пользователя в словарь для JSON.

        Returns:
            Словарь с полями id, name и email.
        """
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
        }

    def __str__(self) -> str:
        """Вернуть имя и почту пользователя."""
        return f"{self.name} <{self.email}>"
