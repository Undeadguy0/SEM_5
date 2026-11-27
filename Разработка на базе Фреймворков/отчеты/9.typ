#import "@local/mirea_title_list:1.0.0": *
#import "@local/gost:1.0.0": *
#import "@preview/codly:2.0.0" as codly

#show: make-gost
#show: codly.theme("dark")
#show raw.where(block: true): codly.new

// Заглушка под скриншот: заменить на #figure(image("..."), caption: [...])
#let shot(what) = block(
  width: 100%,
  inset: 8pt,
  stroke: (paint: red, dash: "dashed"),
  text(fill: red)[*СКРИНШОТ:* #what],
)
#let todo(what) = text(fill: red)[*TODO:* #what]

#titlepage(
  discipline: "Разработка приложений на базе фреймворков",
  group: "ЭФБО-16-24",
  number: 9,
  teacher: "Ящун Т.В.",
  teacher-position: "доц.",
  student: "Бунто М. В.",
  topic: "МОДЕЛИ DJANGO, СВЯЗИ И ОПЕРАЦИИ С БАЗОЙ ДАННЫХ ЧЕРЕЗ ORM",
  year: 2026,
)

*Тема проекта:* система бронирования переговорных комнат (Roomly)

*Коммиты гит:* c42ab9d, 6c240f1

= Цель работы

Освоить описание моделей Django и связей между ними, создание и применение миграций и операции с данными через Django ORM; перевести слой доступа к данным Roomly с ручных SQL-запросов и `sqlite3` на ORM, сохранив работу ранее реализованных страниц.

= Доработка индивидуального проекта

== Модели и связи

По таблицам базы ПР7 описаны три модели: `Room` (`rooms/models.py`), `User` (`users/models.py`, отдельное приложение `users`; это организатор, а не модель аутентификации Django) и `Booking` (`bookings/models.py`). У всех моделей `Meta.ordering`, `verbose_name` и `__str__()`; у `Room` сохранён метод `is_suitable_for()`. `Booking` связана с `Room` и `User` отношением «многие к одному» через `ForeignKey` с `on_delete=PROTECT` и `related_name="bookings"`; метод `cancel()` меняет только признак отмены.

```python
class Room(models.Model):
    """Переговорная комната."""

    name = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Название помещения",
    )
    capacity = models.PositiveIntegerField(
        verbose_name="Вместимость",
    )
    equipment = models.TextField(
        blank=True,
        default="",
        verbose_name="Оборудование",
    )

    class Meta:
        """Сортировка и названия модели."""

        ordering = ["name"]
        verbose_name = "Помещение"
        verbose_name_plural = "Помещения"
```

```python
class User(models.Model):
    """Организатор бронирования.

    Это не встроенная модель аутентификации Django.
    """

    name = models.CharField(
        max_length=200,
        verbose_name="Имя пользователя",
    )
    email = models.EmailField(
        verbose_name="Электронная почта",
    )

    class Meta:
        """Сортировка и названия модели."""

        ordering = ["name"]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
```

```python
class Booking(models.Model):
    """Бронирование помещения пользователем."""

    room = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        related_name="bookings",
        verbose_name="Помещение",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="bookings",
        verbose_name="Пользователь",
    )
    booking_date = models.DateField(
        verbose_name="Дата бронирования",
    )
    start_time = models.CharField(
        max_length=5,
        verbose_name="Время начала",
    )
    end_time = models.CharField(
        max_length=5,
        verbose_name="Время окончания",
    )
    topic = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Тема",
    )
    is_cancelled = models.BooleanField(
        default=False,
        verbose_name="Бронирование отменено",
    )

    class Meta:
        """Сортировка и названия модели."""

        ordering = ["booking_date", "pk"]
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"

    def cancel(self) -> None:
        """Отменить бронирование и сохранить только этот признак."""
        self.is_cancelled = True
        self.save(update_fields=["is_cancelled"])

    def __str__(self) -> str:
        """Вернуть помещение, дату и организатора."""
        return f"{self.room} — {self.booking_date} ({self.user})"
```

== Миграции

Созданы начальные миграции `rooms/0001_initial`, `users/0001_initial`, `bookings/0001_initial`. Отдельным коммитом 6c240f1 проверен цикл изменения структуры: временное поле `Room.n` добавлено миграцией `0002_room_n` и удалено миграцией `0003_remove_room_n`.

```python
class Migration(migrations.Migration):

    dependencies = [
        ("rooms", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="room",
            name="n",
            field=models.CharField(default="example", max_length=20),
            preserve_default=False,
        ),
    ]
```

```bash
$ python manage.py sqlmigrate bookings 0001
BEGIN;
--
-- Create model Booking
--
CREATE TABLE "bookings_booking" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "booking_date" date NOT NULL, "start_time" varchar(5) NOT NULL, "end_time" varchar(5) NOT NULL, "topic" varchar(200) NOT NULL, "is_cancelled" bool NOT NULL, "room_id" bigint NOT NULL REFERENCES "rooms_room" ("id") DEFERRABLE INITIALLY DEFERRED, "user_id" bigint NOT NULL REFERENCES "users_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE INDEX "bookings_booking_room_id_6f0fa517" ON "bookings_booking" ("room_id");
CREATE INDEX "bookings_booking_user_id_834dfc23" ON "bookings_booking" ("user_id");
COMMIT;
```

== Стратегия перехода и перенос данных

Миграции не применяются к базе ПР7: ORM работает с отдельной базой `db.sqlite3`, а `data/roomly.sqlite` остаётся источником. Структура источника просматривается скриптом `db/inspect_source_db.py` (только чтение). Перенос выполняет `db/import_sqlite_to_orm.py`: в одной транзакции `update_or_create()` по исходным `id` (связи сохраняются), строка даты превращается в `date`, `0/1` — в `bool`, затем счётчики `sqlite_sequence` сдвигаются за максимальный `id`.

```python
    with transaction.atomic():
        for row in rooms:
            Room.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "name": row["name"],
                    "capacity": row["capacity"],
                    "equipment": row["equipment"],
                },
            )
        for row in users:
            User.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "name": row["name"],
                    "email": row["email"],
                },
            )
        for row in bookings:
            Booking.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "room_id": row["room_id"],
                    "user_id": row["user_id"],
                    "booking_date": date.fromisoformat(
                        row["booking_date"],
                    ),
                    "start_time": row["start_time"],
                    "end_time": row["end_time"],
                    "topic": row["topic"],
                    "is_cancelled": bool(row["is_cancelled"]),
                },
            )
        _sync_sequence(Room)
        _sync_sequence(User)
        _sync_sequence(Booking)
```

Проверка перенесённых данных и связей в `python manage.py shell`:

```python
from bookings.models import Booking
from rooms.models import Room
from users.models import User

print(Room.objects.count(), User.objects.count(), Booking.objects.count())
for b in Booking.objects.select_related("room", "user"):
    print(b.pk, b.booking_date, b.room.name, b.user.name, b.is_cancelled)
room = Room.objects.get(pk=1)
print(room, room.bookings.count())
```

```bash
3 2 2
2 2026-02-23 Переговорная «Альфа» Михаил False
1 2026-09-29 Переговорная «Альфа» Иванов И.И. False
Переговорная «Альфа» 2
```

== Операции ORM и адаптированные представления

Представления помещений и бронирований больше не вызывают `sqlite3`. Список бронирований (`bookings/views.py`): фильтры по дате, помещению, пользователю и теме из GET-параметров, сортировка через словарь допустимых полей `SORT_FIELDS`, поля связанных моделей через `annotate(F(...))`, постраничный вывод `Paginator` по 5 записей:

```python
def bookings(request: HttpRequest) -> HttpResponse:
    """Показать активные бронирования с фильтрами и страницами."""
    booking_date = request.GET.get("date", "").strip()
    room_id = request.GET.get("room", "").strip()
    user_id = request.GET.get("user", "").strip()
    query = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "date")
    error = None
    if sort not in SORT_FIELDS:
        sort = "date"

    bookings_data = Booking.objects.filter(is_cancelled=False)
    if booking_date:
        try:
            selected_date = datetime.strptime(
                booking_date,
                "%Y-%m-%d",
            ).date()
        except ValueError:
            error = "Укажите корректную дату."
        else:
            bookings_data = bookings_data.filter(
                booking_date=selected_date,
            )
    if room_id.isdigit():
        bookings_data = bookings_data.filter(room_id=int(room_id))
    if user_id.isdigit():
        bookings_data = bookings_data.filter(user_id=int(user_id))
    if query:
        bookings_data = bookings_data.filter(topic__icontains=query)

    bookings_data = bookings_data.annotate(
        room_name=F("room__name"),
        capacity=F("room__capacity"),
        user_name=F("user__name"),
    ).order_by(SORT_FIELDS[sort], "id")
    bookings_data = bookings_data.values(
        "id",
        "booking_date",
        "start_time",
        "end_time",
        "topic",
        "is_cancelled",
        "room_name",
        "capacity",
        "user_name",
    )
    paginator = Paginator(bookings_data, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {
        "bookings": page_obj,
        "page_obj": page_obj,
        "booking_date": booking_date,
        "selected_room": room_id,
        "selected_user": user_id,
        "query": query,
        "sort": sort,
        "rooms": Room.objects.order_by("name"),
        "users": User.objects.order_by("name"),
        "error": error,
    }
    return render(request, "bookings/booking_list.html", context)
```

Поиск свободных помещений на дату (`rooms/views.py`):

```python
            booked_room_ids = Booking.objects.filter(
                booking_date=selected_date,
                is_cancelled=False,
            ).values_list("room_id", flat=True)
            room_list = Room.objects.exclude(
                pk__in=booked_room_ids,
            ).order_by("name")
```

Статистика — `aggregate()` и `annotate()` с условием `filter=Q(...)`, чтобы помещения и пользователи без броней не выпадали из результата:

```python
def statistics(request: HttpRequest) -> HttpResponse:
    """Показать сводку, группировки и помещения с несколькими бронями."""
    bookings_count = Booking.objects.filter(is_cancelled=False).count()
    summary = Room.objects.aggregate(
        rooms_count=Count("id"),
        average_capacity=Avg("capacity"),
        max_capacity=Max("capacity"),
    )
    by_room = Room.objects.annotate(
        bookings_count=Count(
            "bookings",
            filter=Q(bookings__is_cancelled=False),
        ),
        room_name=F("name"),
    ).values(
        "room_name",
        "bookings_count",
    ).order_by("-bookings_count", "room_name")
    popular = by_room.filter(bookings_count__gt=1)
    by_user = User.objects.annotate(
        bookings_count=Count(
            "bookings",
            filter=Q(bookings__is_cancelled=False),
        ),
        user_name=F("name"),
    ).values(
        "user_name",
        "bookings_count",
    ).order_by("-bookings_count", "user_name")
```

ORM-выражения проекта по видам из таблицы 1 методички:

#table(
  columns: (auto, 1fr),
  [*Вид*], [*Выражения в коде (c42ab9d)*],
  [Базовое получение],
  [`Room.objects.order_by("name")`; `get_object_or_404(Room, pk=room_id)`; `get_object_or_404(Booking.objects.select_related(...), pk=booking_id)`],

  [Фильтрация],
  [`Booking.objects.filter(is_cancelled=False)`; `.filter(booking_date=...)`, `.filter(room_id=...)`, `.filter(user_id=...)`; `.filter(capacity__gte=8)`; `Booking.objects.filter(room=room, booking_date=today, is_cancelled=False)`; `Room.objects.exclude(pk__in=...)`; по полю связанной модели — `Q(bookings__is_cancelled=False)`],

  [Поиск], [`filter(topic__icontains=query)`; `filter(Q(name__icontains=query) | Q(equipment__icontains=query))`],
  [Сортировка],
  [`order_by("name")`; `order_by(SORT_FIELDS[sort], "id")` (в т.ч. `room__name`, `user__name`); `order_by("-bookings_count", "room_name")`],

  [Связи],
  [`select_related("room", "user")`; `annotate(room_name=F("room__name"), user_name=F("user__name"))`; `values_list("room_id", flat=True)`],

  [Агрегирование],
  [`Room.objects.aggregate(Count, Avg, Max)`; `Room.objects.annotate(bookings_count=Count(...))`; `User.objects.annotate(...)`; `.count()`],

  [Пагинация], [`Paginator(bookings_data, PAGE_SIZE).get_page(...)`],
)

На странице помещений добавлен поиск по названию и оборудованию, на странице бронирований — форма фильтров, сортировки и навигация по страницам с сохранением параметров. Модели зарегистрированы в админке (`list_display`, `search_fields`). README.md обновлён: модели, команды `migrate` и `python -m db.import_sqlite_to_orm`, проверки.


= Результат работы

Описаны модели `Room`, `User`, `Booking`, связи «многие к одному» настроены внешними ключами, миграции созданы и применены, данные перенесены из базы ПР7 с сохранением `id` и связей, операции с данными выполняются через ORM, страницы и сценарии ПР5–ПР7 работают, добавлены фильтрация, поиск, сортировка и пагинация.

= Проверка

Проверки выполнены на чистой копии коммита c42ab9d после `migrate` и переноса данных; состояние миграций `rooms` после 6c240f1 приведено отдельно.

#[
  ```bash
    $ python manage.py check
  System check identified no issues (0 silenced).
  ```

  ```bash
    $ python manage.py showmigrations rooms bookings users
  rooms
   [X] 0001_initial
  bookings
   [X] 0001_initial
  users
   [X] 0001_initial
  ```

  ```bash
    $ python manage.py showmigrations rooms
  rooms
   [X] 0001_initial
   [X] 0002_room_n
   [X] 0003_remove_room_n
  ```

  ```bash
    $ python manage.py makemigrations --check --dry-run
  No changes detected
  ```

  ```bash
    $ pytest -v
  ============================= test session starts ==============================
  platform linux -- Python 3.13.5, pytest-9.2.0, pluggy-1.7.0 -- venv/bin/python3
  cachedir: .pytest_cache
  rootdir: Разработка на базе Фреймворков
  configfile: pyproject.toml
  testpaths: tests
  collecting ... collected 41 items

  tests/test_bookings.py::test_is_room_available_empty PASSED              [  2%]
  tests/test_bookings.py::test_one_active_booking_per_room_and_date PASSED [  4%]
  tests/test_bookings.py::test_create_booking_rejects_bad_interval PASSED  [  7%]
  tests/test_bookings.py::test_create_booking_fields PASSED                [  9%]
  tests/test_bookings.py::test_cancel_booking_keeps_object PASSED          [ 12%]
  tests/test_bookings.py::test_find_booking_by_id PASSED                   [ 14%]
  tests/test_bookings.py::test_get_booking_status PASSED                   [ 17%]
  tests/test_bookings.py::test_find_bookings_by_organizer PASSED           [ 19%]
  tests/test_bookings.py::test_get_room_schedule PASSED                    [ 21%]
  tests/test_models.py::test_room_attributes_and_methods PASSED            [ 24%]
  tests/test_models.py::test_room_from_data_and_to_dict PASSED             [ 26%]
  tests/test_models.py::test_room_without_equipment PASSED                 [ 29%]
  tests/test_models.py::test_user_from_data_and_str PASSED                 [ 31%]
  tests/test_models.py::test_booking_links_objects_and_cancel PASSED       [ 34%]
  tests/test_rooms.py::test_add_room PASSED                                [ 36%]
  tests/test_rooms.py::test_add_room_assigns_next_id PASSED                [ 39%]
  tests/test_rooms.py::test_find_room_by_id PASSED                         [ 41%]
  tests/test_rooms.py::test_find_room PASSED                               [ 43%]
  tests/test_rooms.py::test_check_room_capacity PASSED                     [ 46%]
  tests/test_rooms.py::test_filter_rooms_by_equipment PASSED               [ 48%]
  tests/test_rooms.py::test_filter_rooms_by_capacity PASSED                [ 51%]
  tests/test_rooms.py::test_sort_rooms PASSED                              [ 53%]
  tests/test_storage.py::test_rooms_roundtrip_keeps_id PASSED              [ 56%]
  tests/test_storage.py::test_users_roundtrip PASSED                       [ 58%]
  tests/test_storage.py::test_load_missing_files PASSED                    [ 60%]
  tests/test_storage.py::test_load_broken_json PASSED                      [ 63%]
  tests/test_storage.py::test_load_wrong_shape PASSED                      [ 65%]
  tests/test_storage.py::test_bookings_roundtrip_links_objects PASSED      [ 68%]
  tests/test_storage.py::test_load_bookings_skips_missing_links PASSED     [ 70%]
  tests/test_users.py::test_add_user PASSED                                [ 73%]
  tests/test_users.py::test_find_user_by_name PASSED                       [ 75%]
  tests/test_users.py::test_find_users_by_substring PASSED                 [ 78%]
  tests/test_web.py::test_index_has_navigation PASSED                      [ 80%]
  tests/test_web.py::test_room_list_and_detail PASSED                      [ 82%]
  tests/test_web.py::test_booking_list_and_detail PASSED                   [ 85%]
  tests/test_web.py::test_available_rooms_by_date PASSED                   [ 87%]
  tests/test_web.py::test_statistics_page PASSED                           [ 90%]
  tests/test_web.py::test_unknown_url_uses_custom_404 PASSED               [ 92%]
  tests/test_web.py::test_room_search_by_name_and_equipment PASSED         [ 95%]
  tests/test_web.py::test_available_rooms_reject_bad_date PASSED           [ 97%]
  tests/test_web.py::test_booking_filters_sort_and_search PASSED           [100%]

  ============================== 41 passed in 0.11s ==============================
  ```

  ```bash
  $ flake8 . --extend-exclude=venv
  ```
]

= Git

Коммиты: `c42ab9d` — «PR9: переход на Django ORM»; `6c240f1` — «chore(rooms): add migrations adding and removing temporary Room.n field».

= Вывод

В результате выполнения ПР9 слой доступа к данным Roomly переведён с `sqlite3` на Django ORM: структура базы описана моделями и управляется миграциями, данные ПР7 перенесены без потери связей, а представления получают данные через QuerySet и передают объекты моделей в шаблоны.

= Ответы на контрольные вопросы

+ *Что такое Django ORM и какую задачу он решает?* \
  Слой, который отображает классы Python на таблицы базы и строит SQL сам. Код работает с объектами моделей вместо ручных запросов через `sqlite3`.
+ *Как модель Django связана с таблицей реляционной базы данных?* \
  Класс модели — таблица, атрибут-поле — столбец, объект — строка. Имя таблицы по умолчанию `приложение_модель`: `rooms_room`, `bookings_booking`.
+ *Как Django определяет первичный ключ модели, если он явно не объявлен?* \
  Добавляет автоинкрементное поле `id` типа `DEFAULT_AUTO_FIELD`; в проекте приложения задают `BigAutoField`.
+ *Чем CharField, TextField, IntegerField, PositiveIntegerField, EmailField и BooleanField отличаются друг от друга?* \
  `CharField` — строка с `max_length`, `TextField` — длинный текст без лимита, `IntegerField` — целое, `PositiveIntegerField` — целое не меньше 0 (вместимость), `EmailField` — строка с проверкой формата почты, `BooleanField` — истина/ложь (`is_cancelled`).
+ *Как в Django реализуется связь «многие к одному»?* \
  Полем `ForeignKey` в модели на стороне «многие»: у `Booking` есть `room` и `user`.
+ *Для чего используется ForeignKey?* \
  Задаёт внешний ключ на другую модель: в таблице появляется столбец `room_id`, а у объекта — доступ к связанному `booking.room`.
+ *Что означают параметры on\_delete и related\_name?* \
  `on_delete` — что делать с бронями при удалении помещения; в проекте `PROTECT` запрещает удаление. `related_name` — имя обратной связи: `room.bookings`, `user.bookings`.
+ *Чем поле модели room отличается от атрибута room\_id?* \
  `room` возвращает объект `Room` (при обращении может выполнить запрос), `room_id` — просто число из столбца, без запроса.
+ *Как получить все записи модели, отфильтровать их и отсортировать?* \
  `Room.objects.all()`, `.filter(capacity__gte=8)`, `.order_by("name")`; методы цепляются друг за друга.
+ *Чем методы get() и filter() отличаются друг от друга?* \
  `get()` возвращает ровно один объект и бросает `DoesNotExist` или `MultipleObjectsReturned`. `filter()` возвращает QuerySet, возможно пустой.
+ *Для чего применяются select\_related() и values\_list()?* \
  `select_related()` подтягивает связанные объекты через JOIN одним запросом (карточка брони). `values_list()` возвращает кортежи или плоский список значений (id занятых помещений при поиске свободных).
+ *Чем создание миграций (makemigrations) отличается от их применения (migrate)?* \
  `makemigrations` по изменениям моделей создаёт файлы миграций, `migrate` выполняет их в базе.
+ *Для чего используется команда sqlmigrate?* \
  Показывает SQL, который выполнит миграция, без её применения.
+ *Почему нельзя без проверки применять миграции к базе, созданной до внедрения Django ORM?* \
  Миграции создают таблицы со своими именами и ограничениями. На старой базе они могут столкнуться с существующими таблицами или не совпасть со структурой, и данные можно повредить. Поэтому база ПР7 сначала изучается (`db/inspect_source_db.py`), а для ORM создаётся отдельная.
+ *Какие способы переноса данных в новую структуру базы данных можно использовать?* \
  Скрипт переноса через ORM, `dumpdata`/`loaddata` с fixture, data-миграция `RunPython`, `inspectdb` и подключение к существующим таблицам, ручной SQL.
+ *Чем objects.create() отличается от создания объекта с последующим вызовом save()?* \
  `objects.create()` создаёт и сохраняет объект одним вызовом. Конструктор и `save()` разделяют создание и запись, между ними можно изменить поля.
+ *Как реализовать поиск свободных помещений средствами ORM?* \
  Взять id помещений с активной бронью на дату и исключить их: `Room.objects.exclude(pk__in=Booking.objects.filter(booking_date=d, is_cancelled=False).values_list("room_id", flat=True))`.
+ *Почему отменённое бронирование не должно блокировать помещение?* \
  Отменённая бронь — история, встреча не состоится. Если её учитывать, помещение будет ложно занято и его нельзя будет забронировать.
+ *Как можно получить количество связанных объектов с помощью ORM?* \
  `room.bookings.count()` для одного объекта или `annotate(bookings_count=Count("bookings", filter=Q(...)))` для набора.
+ *Какие изменения необходимо внести в представления и шаблоны при переходе от словарей к объектам моделей?* \
  Вместо SQL — QuerySet, ключи словаря заменяются атрибутами (`booking.room.name` вместо `room_name`), пустой результат — `get_object_or_404`, даты становятся `date`, `sqlite3.Row` больше не нужен.
+ *В каких случаях удаление объекта может быть запрещено из-за связанных записей?* \
  Когда на объект ссылаются записи с `on_delete=PROTECT`: помещение или пользователя с бронями удалить нельзя (`ProtectedError`).
+ *Почему необходимо проверять не только внешний вид приложения, но и исходный код?* \
  Страница может выглядеть правильно, но внутри остаться `sqlite3`, N+1 запросов, необработанный ввод или неверное условие, которое на текущих данных не проявляется.
+ *Какие сведения необходимо обновить в README.md после перехода к ORM?* \
  Модели и связи, команды `migrate` и переноса данных, где теперь лежит база, как запускать проверки, текущий этап разработки.
+ *Какие преимущества и ограничения есть у ORM по сравнению с выполнением SQL-запросов непосредственно через sqlite3?* \
  Плюсы: независимость от СУБД, защита от инъекций, миграции, связи как атрибуты, повторно используемые QuerySet. Минусы: сложные запросы писать труднее, SQL скрыт и может быть неоптимальным, нужно следить за числом запросов.
