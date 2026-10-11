# Система бронирования переговорных комнат

Консольное приложение и веб-интерфейс Roomly для учёта переговорных комнат офиса. Данные описаны классами и хранятся в JSON. На этом этапе сайт только показывает данные: Django ORM, формы и авторизация не используются.

## Возможности консольной программы

- просмотр и поиск переговорных по названию, вместимости и оборудованию;
- проверка доступности комнаты на дату;
- создание бронирования с указанием организатора, темы и времени;
- отмена бронирования без удаления записи;
- просмотр расписания переговорной на дату;
- поиск бронирований по имени организатора.

На одну дату у комнаты может быть только одно активное бронирование. Отменённое бронирование комнату не занимает.

## Веб-страницы

| Страница | URL | View |
| --- | --- | --- |
| Главная | `/` | `homepage.views.index` |
| Список помещений | `/rooms/` | `rooms.views.rooms` |
| Помещение | `/rooms/<id>/` | `rooms.views.room_detail` |
| Список бронирований | `/bookings/` | `bookings.views.bookings` |
| Бронирование | `/bookings/<id>/` | `bookings.views.booking_detail` |

Неизвестный адрес обрабатывает `homepage.views.page_not_found` и возвращает статус 404. Если помещение или бронирование не найдены, карточка тоже отвечает статусом 404.

Страницы собирает функция `page()`: общая вёрстка, кодировка UTF-8, метатег viewport, Bootstrap 5.3 с CDN и навигация. Карточка помещения показывает, свободна ли комната сегодня: для этого вызывается `is_room_available()` из консольного приложения.

## Классы

| Класс | Атрибуты | Методы |
| --- | --- | --- |
| `Room` | `id`, `name`, `capacity`, `equipment` | `is_suitable_for()`, `has_equipment()`, `from_data()`, `to_dict()`, `__str__()` |
| `User` | `id`, `name`, `email` | `from_data()`, `to_dict()`, `__str__()` |
| `Booking` | `id`, `room`, `user`, `booking_date`, `start_time`, `end_time`, `topic`, `is_cancelled` | `cancel()`, `is_active()`, `to_dict()`, `__str__()` |

`Booking` хранит объекты `Room` и `User`. В JSON записываются `room_id` и `user_id`. При загрузке программа находит объекты по этим номерам. Если комната или пользователь не найдены, бронирование пропускается.

## Структура проекта

- `main.py` — консольное меню;
- `manage.py`, `roomly/` — проект Django;
- `homepage/`, `rooms/`, `bookings/` — приложения сайта;
- `models/` — классы `Room`, `User`, `Booking`;
- `domain/rooms.py`, `domain/bookings.py` — функции предметной области;
- `users.py` — функции работы с пользователями;
- `storage.py` — сохранение и загрузка JSON;
- `utils.py` — ввод числа, даты и времени;
- `data/` — JSON-файлы данных;
- `tests/` — тесты консоли и страниц.

Функции комнат и бронирований лежат в пакете `domain/`, потому что каталоги `rooms/` и `bookings/` заняты приложениями Django.

## Формат данных

`data/rooms.json`: `id`, `name`, `capacity`, `equipment`.

`data/users.json`: `id`, `name`, `email`.

`data/bookings.json`: `id`, `room_id`, `user_id`, `booking_date`, `start_time`, `end_time`, `topic`, `is_cancelled`.

## Требования

- Python 3.12 (в задании указан 3.11, в системе его нет; Django 5.2 поддерживает 3.12)
- Django 5.2
- pytest
- flake8

## Установка зависимостей

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Запуск сайта

```bash
python manage.py runserver
```

Главная страница: http://127.0.0.1:8000/

## Запуск консольной программы

```bash
python main.py
```

## Запуск тестов

```bash
pytest -v
```

## Проверка качества кода

```bash
flake8 . --extend-exclude=venv
```
