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

Страницы рисуют шаблоны Django. Общий каркас — `templates/base.html`: блоки `title` и `content`, кодировка UTF-8, метатег viewport, Bootstrap 5.3 с CDN, свои CSS, JavaScript и логотип. Навигация подключена через `{% include "includes/navigation.html" %}`. Ссылки собраны тегом `{% url %}` с пространствами имён `homepage`, `rooms` и `bookings`.

Списки обходят контекст циклом `{% for %}`, пустую коллекцию обрабатывает `{% empty %}`. Статус бронирования и доступность комнаты на сегодня выводятся через `{% if %}`. Число записей показывает фильтр `length`, пустое название — фильтр `default`. Карточка помещения — `rooms/includes/room_card.html`, значок статуса — `bookings/includes/booking_status.html`. Доступность на сегодня считает `is_room_available()`, текст статуса — `get_booking_status()`. Год в подвале подставляет `main.js`.

View-функции передают данные словарём контекста в `render()`. HTML в Python больше не собирается.

## Шаблоны и статические файлы

- `templates/base.html` — базовый шаблон, `{% extends %}` и `{% block %}`;
- `templates/includes/navigation.html` — общее меню;
- `homepage/templates/homepage/` — главная и страницы 404;
- `rooms/templates/rooms/room_list.html`, `room_detail.html`;
- `rooms/templates/rooms/includes/room_card.html` — карточка одного помещения;
- `bookings/templates/bookings/booking_list.html`, `booking_detail.html`;
- `bookings/templates/bookings/includes/booking_status.html` — активно или отменено;
- `homepage/static/homepage/css/style.css` — стили `.room-card`, `.booking-status`, `.roomly-logo`;
- `homepage/static/homepage/js/main.js` — текущий год в `#current-year`;
- `homepage/static/homepage/img/logo.png` — логотип.

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
- `homepage/`, `rooms/`, `bookings/` — приложения сайта, их шаблоны и статика;
- `templates/` — базовый шаблон и общая навигация;
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

Сайт показывает помещения и бронирования из JSON. Страницы собраны шаблонами Django: базовый шаблон, наследование, include, контекст и статические файлы. Django ORM, формы и операции создания через сайт на этом этапе не используются.

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
