"""Функции работы с пользователями."""

from models import User


def add_user(users: list[User], name: str, email: str) -> User:
    """Добавить пользователя в список users.

    Args:
        users: Список пользователей.
        name: Имя.
        email: Электронная почта.

    Returns:
        Созданный объект User.
    """
    new_id = max((user.id for user in users), default=0) + 1
    user = User(new_id, name, email)
    users.append(user)
    return user


def get_user_by_id(users: list[User], user_id: int) -> User | None:
    """Найти пользователя по идентификатору.

    Args:
        users: Список пользователей.
        user_id: Идентификатор.

    Returns:
        Объект User или None.
    """
    for user in users:
        if user.id == user_id:
            return user
    return None


def find_user_by_name(users: list[User], name: str) -> User | None:
    """Найти пользователя по точному имени без учёта регистра.

    Args:
        users: Список пользователей.
        name: Имя организатора.

    Returns:
        Объект User или None, если совпадения нет.
    """
    needle = name.strip().lower()
    for user in users:
        if user.name.lower() == needle:
            return user
    return None


def find_users(users: list[User], query: str) -> list[User]:
    """Найти пользователей по подстроке имени.

    Args:
        users: Список пользователей.
        query: Подстрока поиска, без учёта регистра.

    Returns:
        Список подходящих пользователей.
    """
    query_lower = query.lower()
    return [user for user in users if query_lower in user.name.lower()]
