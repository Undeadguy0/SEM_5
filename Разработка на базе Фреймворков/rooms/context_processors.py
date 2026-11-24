"""Общие данные Roomly для шаблонов."""

from rooms.models import Room


def room_context(request):
    """Передать название сайта и число помещений.

    Args:
        request: Текущий HTTP-запрос.

    Returns:
        Словарь, который Django добавляет в контекст шаблона.
    """
    return {
        "site_name": "Roomly",
        "rooms_count": Room.objects.count(),
    }
