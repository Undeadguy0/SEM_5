# Система бронирования переговорных комнат

Консольное приложение и веб-интерфейс Roomly для учёта переговорных комнат офиса. Данные описаны классами. Консоль хранит их в JSON. Страницы сайта читают Django ORM из `db.sqlite3`. Формы создания и авторизация не используются. Файл `data/roomly.sqlite` и каталог `sql/` остаются слоем ПР7: представления их больше не вызывают.

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
| Свободные помещения | `/rooms/available/` | `rooms.views.available_rooms` |
| Помещение | `/rooms/<id>/` | `rooms.views.room_detail` |
| Список бронирований | `/bookings/` | `bookings.views.bookings` |
| Статистика | `/bookings/statistics/` | `bookings.views.statistics` |
| Бронирование | `/bookings/<id>/` | `bookings.views.booking_detail` |

Неизвестный адрес обрабатывает `homepage.views.page_not_found` и возвращает статус 404. Если помещение или бронирование не найдены, карточка тоже отвечает статусом 404.

Страницы рисуют шаблоны Django. Общий каркас — `templates/base.html`: блоки `title` и `content`, кодировка UTF-8, метатег viewport, Bootstrap 5.3 с CDN, свои CSS, JavaScript и логотип. Навигация подключена через `{% include "includes/navigation.html" %}`: Главная, Помещения, Бронирования, Статистика. Ссылки собраны тегом `{% url %}` с пространствами имён `homepage`, `rooms` и `bookings`. На списке помещений есть ссылка «Найти свободное помещение».

Списки обходят контекст циклом `{% for %}`, пустую коллекцию обрабатывает `{% empty %}`. Статус бронирования и доступность комнаты на сегодня выводятся через `{% if %}`. Число записей показывает фильтр `length`, пустое название — фильтр `default`. Карточка помещения — `rooms/includes/room_card.html`, значок статуса — `bookings/includes/booking_status.html`. Доступность на сегодня считает запрос активных бронирований на текущую дату, текст статуса — `get_booking_status()`. Список бронирований фильтруется по дате, помещению, пользователю и теме, сортируется по белому списку полей и разбивается на страницы по 5 записей. Год в подвале подставляет `main.js`.

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
- `homepage/`, `rooms/`, `users/`, `bookings/` — приложения сайта, их модели, миграции, шаблоны и статика;
- `templates/` — базовый шаблон и общая навигация;
- `models/` — классы `Room`, `User`, `Booking`;
- `domain/rooms.py`, `domain/bookings.py` — функции предметной области;
- `users/directory.py` — функции консоли для пользователей, их реэкспортирует пакет `users`;
- `storage.py` — сохранение и загрузка JSON;
- `utils.py` — ввод числа, даты и времени;
- `data/` — JSON-файлы и база `roomly.sqlite`;
- `sql/schema.sql` — команды создания таблиц;
- `sql/queries.sql` — SQL-запросы проекта;
- `db/database.py` — подключение к SQLite слоя ПР7;
- `db/import_json.py` — перенос JSON в таблицы ПР7;
- `db/import_sqlite_to_orm.py` — перенос `data/roomly.sqlite` в модели Django;
- `db/inspect_source_db.py` — просмотр таблиц исходной базы, только чтение;
- `tests/` — тесты консоли и страниц.

Функции комнат и бронирований лежат в пакете `domain/`, потому что каталоги `rooms/` и `bookings/` заняты приложениями Django.

## Формат данных

`data/rooms.json`: `id`, `name`, `capacity`, `equipment`.

`data/users.json`: `id`, `name`, `email`.

`data/bookings.json`: `id`, `room_id`, `user_id`, `booking_date`, `start_time`, `end_time`, `topic`, `is_cancelled`.

## База данных

Сайт читает `db.sqlite3` через Django ORM. Файл создаёт `migrate`, в репозиторий он не входит. Исходные данные ПР7 лежат в `data/roomly.sqlite`. Перед первым запуском их переносят в ORM с сохранением первичных ключей.

### Модели Django

| Модель | Приложение | Поля | Связи |
| --- | --- | --- | --- |
| `Room` | `rooms` | `name`, `capacity`, `equipment` | — |
| `User` | `users` | `name`, `email` | это не пользователь `django.contrib.auth` |
| `Booking` | `bookings` | `booking_date`, `start_time`, `end_time`, `topic`, `is_cancelled` | `room` и `user`: `on_delete=PROTECT`, `related_name="bookings"` |

`equipment` — строка через запятую. Время хранится как `HH:MM`. Отменённое бронирование комнату не занимает. `Booking.cancel()` ставит признак отмены. `Room.is_suitable_for()` сравнивает вместимость с числом участников.

Миграции лежат в `rooms/migrations/`, `users/migrations/` и `bookings/migrations/`.

### Перенос в ORM

Локальная копия исходного файла на случай отката: `data/roomly_backup.sqlite`. В git она не входит.

```bash
python manage.py makemigrations
python manage.py migrate
python -m db.import_sqlite_to_orm
```

`db/import_sqlite_to_orm.py` читает `data/roomly.sqlite` и вызывает `update_or_create()` с прежними `id`. Вместе с общими столбцами переносятся оборудование, время и тема.

Страницы после переноса:

- список помещений: сортировка по имени, поиск по названию или оборудованию, отбор `capacity` от 8;
- свободные помещения: `exclude()` комнат с активным бронированием на дату;
- карточка помещения: `get_object_or_404` и число активных броней на сегодня;
- список бронирований: фильтры, поиск темы, сортировка по белому списку, пагинация;
- карточка бронирования: `select_related("room", "user")`;
- статистика: `count`, `aggregate`, `annotate` и отбор помещений с числом броней больше одного;
- главная: число помещений и число активных бронирований.

### Слой SQLite ПР7

Файл `data/roomly.sqlite`, схема `sql/schema.sql`, пятнадцать запросов в `sql/queries.sql`, подключение `db/database.py` и перенос JSON `db/import_json.py` сохранены. Представления их не импортируют.

| Таблица | Поля | Ключи |
| --- | --- | --- |
| `rooms` | `id`, `name`, `capacity`, `equipment` | `id` — первичный ключ |
| `users` | `id`, `name`, `email` | `id` — первичный ключ |
| `bookings` | `id`, `room_id`, `user_id`, `booking_date`, `start_time`, `end_time`, `topic`, `is_cancelled` | `room_id` → `rooms.id`, `user_id` → `users.id` |

`db/database.py` включает `PRAGMA foreign_keys = ON` и `sqlite3.Row`. Значения передаются параметрами `?`. Повторный перенос JSON:

```bash
python -m db.import_json
```

## Текущий этап разработки

На ПР9 страницы Roomly переведены на Django ORM:

- модели `Room`, `User` и `Booking` связаны внешними ключами `PROTECT`;
- миграции описывают таблицы в `db.sqlite3`;
- данные перенесены из `data/roomly.sqlite` с сохранением `id`;
- представления не вызывают `sqlite3`;
- на списках есть поиск, фильтры, сортировка и пагинация.

JSON и консольная программа сохранены. Формы создания бронирования на сайте нет.

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
python manage.py migrate
python -m db.import_sqlite_to_orm
python manage.py runserver
```

Главная страница: http://127.0.0.1:8000/

Сайт показывает помещения и бронирования из `db.sqlite3`. Страницы собраны шаблонами Django. Формы создания и операции записи через сайт не используются.

## Запуск консольной программы

```bash
python main.py
```

## Запуск тестов

```bash
pytest -v
```

## Проверка

```bash
python manage.py check
python manage.py showmigrations
python manage.py makemigrations --check
pytest -v
flake8 . --extend-exclude=venv
```
