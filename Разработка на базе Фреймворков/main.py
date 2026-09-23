from datetime import datetime, timedelta
from typing import Tuple


def is_available(
    t1_start: datetime, t2_start: datetime, t1_duration: int, t2_duration: int
) -> bool:
    """
    Функция, определяющая доступность слота по последней брони + продолжительность обоих.
    Durations - МИНУТЫ!!
    """
    t1_end = t1_start + timedelta(minutes=t1_duration)
    t2_end = t2_start + timedelta(minutes=t2_duration)

    is_overlapping = (t1_start < t2_end) and (t2_start < t1_end)

    return not is_overlapping


def check_capacity(room_capacity: int, required_seats: int) -> Tuple[bool, str]:
    """
    Проверяет, достаточно ли мест в переговорной комнате.
    Возвращает доступность и строку с ошибкой, если произошла
    """
    if required_seats <= 0:
        return (False, "Ошибка: количество участников должно быть больше нуля")

    if required_seats > room_capacity:
        return (False, "")
    return (True, "")


def calculate_booking_cost(duration_minutes: int, rate_per_hour: float) -> float:
    """
    Рассчитывает стоимость бронирования на основе длительности и почасовой ставки.
    """
    if duration_minutes <= 0:
        return 0.0

    duration_hours = duration_minutes / 60
    total_cost = duration_hours * rate_per_hour

    return round(total_cost, 2)
