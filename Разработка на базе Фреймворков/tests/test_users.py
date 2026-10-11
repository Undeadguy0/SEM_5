"""Тесты для модуля users.py."""

from models import User
from users import add_user, find_user_by_name, find_users, get_user_by_id


def test_add_user():
    users: list[User] = []
    created = add_user(users, "Иванов И.И.", "ivanov@example.com")
    assert created.id == 1
    assert len(users) == 1
    assert get_user_by_id(users, 1) is created
    assert get_user_by_id(users, 9) is None


def test_find_user_by_name():
    users = [
        User(1, "Иванов И.И.", "ivanov@example.com"),
        User(2, "Петров П.П.", "petrov@example.com"),
    ]
    found = find_user_by_name(users, "  иванов и.и. ")
    assert found is users[0]
    assert find_user_by_name(users, "Иванов") is None


def test_find_users_by_substring():
    users = [
        User(1, "Иванов И.И.", "ivanov@example.com"),
        User(2, "Иванова А.А.", "a@example.com"),
        User(3, "Петров П.П.", "petrov@example.com"),
    ]
    result = find_users(users, "иванов")
    assert [user.id for user in result] == [1, 2]
    assert find_users(users, "сидоров") == []
