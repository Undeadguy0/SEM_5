"""Подключение к базе SQLite проекта Roomly."""

import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "roomly.sqlite"


def get_connection() -> sqlite3.Connection:
    """Открыть базу, включить внешние ключи и имена столбцов.

    Returns:
        Соединение с row_factory = sqlite3.Row.
    """
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection
