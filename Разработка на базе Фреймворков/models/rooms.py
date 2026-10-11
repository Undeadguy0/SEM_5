"""Класс переговорной комнаты."""


class Room:
    """Переговорная комната офиса."""

    def __init__(
        self,
        room_id: int,
        name: str,
        capacity: int,
        equipment: list[str] | None = None,
    ) -> None:
        """Создать переговорную.

        Args:
            room_id: Идентификатор комнаты.
            name: Название.
            capacity: Вместимость, человек.
            equipment: Список оборудования.
        """
        self.id = room_id
        self.name = name
        self.capacity = capacity
        if equipment is None:
            self.equipment = []
        else:
            self.equipment = list(equipment)

    def is_suitable_for(self, people_count: int) -> bool:
        """Проверить, хватает ли мест для people_count человек.

        Args:
            people_count: Число участников.

        Returns:
            True, если вместимость не меньше people_count.
        """
        return self.capacity >= people_count

    def has_equipment(self, required: list[str]) -> bool:
        """Проверить наличие всего оборудования из required.

        Args:
            required: Требуемое оборудование.

        Returns:
            True, если каждый элемент required есть в комнате.
        """
        owned = {item.lower() for item in self.equipment}
        return all(item.lower() in owned for item in required)

    @classmethod
    def from_data(cls, data: dict) -> "Room":
        """Создать комнату из словаря JSON.

        Args:
            data: Словарь с ключами id, name, capacity и equipment.

        Returns:
            Объект Room.
        """
        equipment = data.get("equipment", [])
        if not isinstance(equipment, list):
            equipment = []
        return cls(
            room_id=int(data["id"]),
            name=str(data["name"]),
            capacity=int(data["capacity"]),
            equipment=[str(item) for item in equipment],
        )

    def to_dict(self) -> dict:
        """Преобразовать комнату в словарь для JSON.

        Returns:
            Словарь с полями id, name, capacity и equipment.
        """
        return {
            "id": self.id,
            "name": self.name,
            "capacity": self.capacity,
            "equipment": list(self.equipment),
        }

    def __str__(self) -> str:
        """Вернуть краткое описание комнаты."""
        return f"{self.name}, {self.capacity} мест"
