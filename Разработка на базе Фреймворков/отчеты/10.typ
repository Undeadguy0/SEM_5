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
  number: 10,
  teacher: "Ящун Т.В.",
  teacher-position: "доц.",
  student: "Бунто М. В.",
  topic: "АДМИНИСТРАТИВНАЯ ПАНЕЛЬ DJANGO И РАБОТА С ДАННЫМИ ЧЕРЕЗ ORM",
  year: 2026,
)

*Тема проекта:* система бронирования переговорных комнат (Roomly)

*Коммит гит:* 049042e

= Цель работы

Освоить возможности административной панели Django и углубить навыки работы с данными через Django ORM на примере индивидуального проекта Roomly — системы бронирования помещений.

= Настройка административной панели

Модели `Room`, `User`, `Booking` зарегистрированы декоратором `@admin.register` с собственными `ModelAdmin`. Интерфейс русифицирован: `verbose_name` у приложений (`RoomsConfig`, `BookingsConfig`, …: «Помещения», «Бронирования», «Пользователи»), у моделей (`Meta.verbose_name`, `verbose_name_plural`) и у полей. Настроены столбцы (`list_display`), ссылки на карточку (`list_display_links`), поиск, фильтры, сортировка, 20 записей на страницу. Вместимость редактируется прямо в списке (`list_editable`), `slug` и `is_large` — только для чтения. На карточках помещения и пользователя связанные бронирования выводятся через `TabularInline`.

```python
class BookingInline(admin.TabularInline):
    """Связанные бронирования на карточке помещения."""

    model = Booking
    fields = ("user", "booking_date", "status")
    extra = 0
    can_delete = False


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    """Список переговорных."""

    list_display = (
        "id",
        "name",
        "slug",
        "capacity",
        "is_large",
    )
    list_display_links = ("name",)
    list_editable = ("capacity",)
    search_fields = ("name", "equipment")
    list_filter = ("capacity", "is_large")
    ordering = ("name",)
    list_per_page = 20
    readonly_fields = ("slug", "is_large")
    inlines = (BookingInline,)
```

```python
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Список бронирований со связями."""

    list_display = (
        "id",
        "room",
        "user",
        "booking_date",
        "status",
    )
    list_display_links = ("id",)
    search_fields = ("topic", "room__name", "user__name")
    list_filter = ("status", "booking_date")
    ordering = ("-booking_date",)
    list_per_page = 20
```

`UserAdmin` устроен так же: `list_display = ("id", "name", "email")`, поиск по имени и почте, inline `UserBookingInline` с полями `room`, `booking_date`, `status`.

= Изменения моделей, миграций и менеджера QuerySet

*Статус бронирования.* Булев `is_cancelled` заменён полем `status` с `TextChoices` (`active`, `cancelled`, `completed`). Переход выполнен тремя миграциями: `0002_booking_status` добавляет поле, data-миграция `0003_migrate_booking_statuses` переносит значения, `0004_remove_booking_is_cancelled` удаляет старое поле. `cancel()` теперь ставит `CANCELLED`, запись не удаляется.

```python
class BookingQuerySet(models.QuerySet):
    """Набор запросов для работы с бронированиями."""

    def active(self):
        """Вернуть только активные бронирования."""
        return self.filter(status=self.model.Status.ACTIVE)

    def cancelled(self):
        """Вернуть только отменённые бронирования."""
        return self.filter(status=self.model.Status.CANCELLED)

    def completed(self):
        """Вернуть только завершённые бронирования."""
        return self.filter(status=self.model.Status.COMPLETED)

    def for_date(self, selected_date):
        """Вернуть бронирования на указанную дату.

        Args:
            selected_date: Дата поля booking_date.
        """
        return self.filter(booking_date=selected_date)


class BookingManager(models.Manager.from_queryset(BookingQuerySet)):
    """Менеджер модели Booking с методами QuerySet."""


class Booking(models.Model):
    """Бронирование помещения пользователем."""

    class Status(models.TextChoices):
        """Состояние бронирования."""

        ACTIVE = "active", "Активно"
        CANCELLED = "cancelled", "Отменено"
        COMPLETED = "completed", "Завершено"

    objects = BookingManager()
...
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name="Статус бронирования",
    )
```

```python
def migrate_booking_statuses(apps, schema_editor):
    """Перенести is_cancelled в status до удаления старого поля."""
    Booking = apps.get_model("bookings", "Booking")
    Booking.objects.filter(is_cancelled=True).update(
        status="cancelled",
    )
    Booking.objects.filter(is_cancelled=False).update(
        status="active",
    )
```

*Помещение.* Добавлены `slug` (транслитерация названия через `unidecode` + `id`, миграции `0004`–`0007`: поле, заполнение `RunPython`, `unique=True`), `get_absolute_url()` и маршрут `<slug:slug>/`, а также вычисляемое базой поле `is_large = GeneratedField(...)` (вместимость от 50 мест).

```python
    is_large = models.GeneratedField(
        expression=Case(
            When(capacity__gte=50, then=Value(True)),
            default=Value(False),
            output_field=models.BooleanField(),
        ),
        output_field=models.BooleanField(),
        db_persist=True,
        verbose_name="Большое помещение",
    )
...
    def save(self, *args, **kwargs):
        """Заполнить slug из названия и первичного ключа."""
        if not self.slug:
            transliterated_name = unidecode(self.name or "")
            base_slug = slugify(transliterated_name) or "room"
            if self.pk:
                self.slug = f"{base_slug}-{self.pk}"
            else:
                super().save(*args, **kwargs)
                self.slug = f"{base_slug}-{self.pk}"
                super().save(update_fields=["slug"])
                return
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Вернуть адрес подробной страницы помещения."""
        return reverse(
            "rooms:detail",
            kwargs={"slug": self.slug},
        )
```

*Контекстный процессор* `rooms.context_processors.room_context` добавляет во все шаблоны `site_name` и `rooms_count`; зарегистрирован в `TEMPLATES` в `settings.py`.

= ORM-запросы: фильтрация, сортировка, пагинация, статистика

Список бронирований начинается с метода менеджера по выбранному статусу; дата фильтруется `for_date()`, помещение, пользователь и тема — `filter()`, сортировка идёт только по полям из `SORT_FIELDS`, страница — `Paginator` по 5 записей. Шаблон списка сохраняет параметры фильтра в ссылках пагинации. Неверные статус и дата дают сообщение, а не ошибку 500.

```python
SORT_FIELDS = {
    "date": "booking_date",
    "room": "room__name",
    "user": "user__name",
}
STATUS_FILTERS = {
    "active": Booking.objects.active,
    "cancelled": Booking.objects.cancelled,
    "completed": Booking.objects.completed,
}
PAGE_SIZE = 5


def bookings(request: HttpRequest) -> HttpResponse:
    """Показать бронирования с фильтрами и страницами."""
    booking_date = request.GET.get("date", "").strip()
    room_id = request.GET.get("room", "").strip()
    user_id = request.GET.get("user", "").strip()
    query = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "date")
    status = request.GET.get("status", "").strip() or "active"
    errors = []
    if sort not in SORT_FIELDS:
        sort = "date"
    if status not in STATUS_FILTERS:
        errors.append("Укажите корректный статус.")
        status = "active"

    bookings_data = STATUS_FILTERS[status]()
    if booking_date:
        try:
            selected_date = datetime.strptime(
                booking_date,
                "%Y-%m-%d",
            ).date()
        except ValueError:
            errors.append("Укажите корректную дату.")
        else:
            bookings_data = bookings_data.for_date(selected_date)
```

Статистика по статусам — один `aggregate()` с условными `Count`; число активных броней по помещениям и организаторам — `annotate(Count(..., filter=Q(bookings__status=ACTIVE)))`:

```python
def statistics(request: HttpRequest) -> HttpResponse:
    """Показать сводку по статусам, помещениям и организаторам."""
    status_stats = Booking.objects.aggregate(
        total_bookings=Count("id"),
        active_bookings=Count(
            "id",
            filter=Q(status=Booking.Status.ACTIVE),
        ),
        cancelled_bookings=Count(
            "id",
            filter=Q(status=Booking.Status.CANCELLED),
        ),
        completed_bookings=Count(
            "id",
            filter=Q(status=Booking.Status.COMPLETED),
        ),
    )
```

= Доступность помещений с учётом статусов

Свободные помещения и занятость на сегодня считаются по `Booking.objects.active().for_date(...)`, поэтому отменённые и завершённые брони помещение не блокируют. Проверка в `python manage.py shell` на копии базы (после проверки статус возвращён):

```python
from datetime import date

from django.db.models import Count, Q

from bookings.models import Booking
from rooms.models import Room

day = date(2026, 9, 29)


def free_rooms():
    busy = Booking.objects.active().for_date(day).values_list("room_id", flat=True)
    return [str(room) for room in Room.objects.exclude(pk__in=busy)]


print("Свободны:", free_rooms())
booking = Booking.objects.get(pk=1)
booking.cancel()
print("Бронь 1:", booking.get_status_display())
print("Свободны:", free_rooms())
print(Booking.objects.aggregate(
    active=Count("id", filter=Q(status=Booking.Status.ACTIVE)),
    cancelled=Count("id", filter=Q(status=Booking.Status.CANCELLED)),
))
booking.status = Booking.Status.ACTIVE
booking.save(update_fields=["status"])
```

```bash
Свободны: ['Без названия', 'Переговорная «Гамма»']
Бронь 1: Отменено
Свободны: ['Без названия', 'Переговорная «Альфа»', 'Переговорная «Гамма»']
{'active': 1, 'cancelled': 1}
```

= Анализ SQL-запросов (Django Debug Toolbar)

Подключён `django-debug-toolbar==5.2.0`: приложение `debug_toolbar` и `DebugToolbarMiddleware` в `settings.py`, `INTERNAL_IPS = ["127.0.0.1"]`, маршрут `__debug__/` только при `DEBUG`. Число SQL-запросов по страницам (подсчёт `CaptureQueriesContext` тестовым клиентом на тех же данных):

```bash
/rooms/                                  200  SQL-запросов: 3
/rooms/peregovornaia-alfa-1/             200  SQL-запросов: 3
/rooms/available/?date=2026-09-29        200  SQL-запросов: 2
/bookings/                               200  SQL-запросов: 5
/bookings/?room=1&sort=room              200  SQL-запросов: 5
/bookings/?status=cancelled              200  SQL-запросов: 4
/bookings/1/                             200  SQL-запросов: 2
/bookings/statistics/                    200  SQL-запросов: 7
```

Число запросов не растёт с числом строк: список бронирований берёт помещение и пользователя одним `INNER JOIN` через `annotate(F(...))` + `values()`, карточка брони — через `select_related("room", "user")`, проблемы N+1 нет.

= Проверка

#[
  ```bash
    $ python manage.py check
  System check identified no issues (0 silenced).
  ```

  ```bash
    $ python manage.py showmigrations rooms bookings users
  rooms
   [X] 0001_initial
   [X] 0002_room_n
   [X] 0003_remove_room_n
   [X] 0004_room_slug
   [X] 0005_room_is_large
   [X] 0006_populate_room_slugs
   [X] 0007_room_slug_unique
  bookings
   [X] 0001_initial
   [X] 0002_booking_status
   [X] 0003_migrate_booking_statuses
   [X] 0004_remove_booking_is_cancelled
  users
   [X] 0001_initial
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
  collecting ... collected 42 items

  tests/test_bookings.py::test_is_room_available_empty PASSED              [  2%]
  tests/test_bookings.py::test_one_active_booking_per_room_and_date PASSED [  4%]
  tests/test_bookings.py::test_create_booking_rejects_bad_interval PASSED  [  7%]
  tests/test_bookings.py::test_create_booking_fields PASSED                [  9%]
  tests/test_bookings.py::test_cancel_booking_keeps_object PASSED          [ 11%]
  tests/test_bookings.py::test_find_booking_by_id PASSED                   [ 14%]
  tests/test_bookings.py::test_get_booking_status PASSED                   [ 16%]
  tests/test_bookings.py::test_find_bookings_by_organizer PASSED           [ 19%]
  tests/test_bookings.py::test_get_room_schedule PASSED                    [ 21%]
  tests/test_models.py::test_room_attributes_and_methods PASSED            [ 23%]
  tests/test_models.py::test_room_from_data_and_to_dict PASSED             [ 26%]
  tests/test_models.py::test_room_without_equipment PASSED                 [ 28%]
  tests/test_models.py::test_user_from_data_and_str PASSED                 [ 30%]
  tests/test_models.py::test_booking_links_objects_and_cancel PASSED       [ 33%]
  tests/test_pr10.py::test_status_slug_and_generated_field PASSED          [ 35%]
  tests/test_rooms.py::test_add_room PASSED                                [ 38%]
  tests/test_rooms.py::test_add_room_assigns_next_id PASSED                [ 40%]
  tests/test_rooms.py::test_find_room_by_id PASSED                         [ 42%]
  tests/test_rooms.py::test_find_room PASSED                               [ 45%]
  tests/test_rooms.py::test_check_room_capacity PASSED                     [ 47%]
  tests/test_rooms.py::test_filter_rooms_by_equipment PASSED               [ 50%]
  tests/test_rooms.py::test_filter_rooms_by_capacity PASSED                [ 52%]
  tests/test_rooms.py::test_sort_rooms PASSED                              [ 54%]
  tests/test_storage.py::test_rooms_roundtrip_keeps_id PASSED              [ 57%]
  tests/test_storage.py::test_users_roundtrip PASSED                       [ 59%]
  tests/test_storage.py::test_load_missing_files PASSED                    [ 61%]
  tests/test_storage.py::test_load_broken_json PASSED                      [ 64%]
  tests/test_storage.py::test_load_wrong_shape PASSED                      [ 66%]
  tests/test_storage.py::test_bookings_roundtrip_links_objects PASSED      [ 69%]
  tests/test_storage.py::test_load_bookings_skips_missing_links PASSED     [ 71%]
  tests/test_users.py::test_add_user PASSED                                [ 73%]
  tests/test_users.py::test_find_user_by_name PASSED                       [ 76%]
  tests/test_users.py::test_find_users_by_substring PASSED                 [ 78%]
  tests/test_web.py::test_index_has_navigation PASSED                      [ 80%]
  tests/test_web.py::test_room_list_and_detail PASSED                      [ 83%]
  tests/test_web.py::test_booking_list_and_detail PASSED                   [ 85%]
  tests/test_web.py::test_available_rooms_by_date PASSED                   [ 88%]
  tests/test_web.py::test_statistics_page PASSED                           [ 90%]
  tests/test_web.py::test_unknown_url_uses_custom_404 PASSED               [ 92%]
  tests/test_web.py::test_room_search_by_name_and_equipment PASSED         [ 95%]
  tests/test_web.py::test_available_rooms_reject_bad_date PASSED           [ 97%]
  tests/test_web.py::test_booking_filters_sort_and_search PASSED           [100%]

  ============================== 42 passed in 0.52s ==============================
  ```

  ```bash
  $ flake8 . --extend-exclude=venv
  ```
]

= Git

Коммит `049042e` — «PR10: административная панель и работа с данными через ORM».



= Вывод

В результате выполнения ПР10 для моделей Roomly настроена русифицированная административная панель со списками, поиском, фильтрами и inline-бронированиями; статус брони переведён на `TextChoices` с переносом данных миграцией, повторяющиеся условия вынесены в менеджер QuerySet, помещения получили slug и вычисляемое поле, а запросы страниц проверены через Debug Toolbar. Занятость помещений учитывает только активные бронирования, проверки и тесты проходят.

= Ответы на контрольные вопросы

+ *Для чего предназначена административная панель Django?* \
  Админка Django — готовый интерфейс для просмотра и правки данных моделей теми пользователями, у кого есть права. Гостевые страницы Roomly она не заменяет.
+ *Как зарегистрировать модель в административной панели?* \
  Регистрация: `@admin.register(Room)` над классом `ModelAdmin` или `admin.site.register(Room, RoomAdmin)`. В проекте декоратор.
+ *Для чего используется класс admin.ModelAdmin?* \
  `ModelAdmin` описывает, как модель выглядит в админке: столбцы, поиск, фильтры, порядок, inline. Поля модели он не объявляет.
+ *Как с помощью list\_display настроить столбцы списка записей?* \
  `list_display` перечисляет столбцы списка. Это имена полей, методы модели или методы админки.
+ *Чем search\_fields отличается от list\_filter?* \
  `search_fields` — строка поиска, условие `LIKE` по полям. `list_filter` — боковые фильтры с готовыми значениями. Поиск по связанному полю пишется как `room__name`.
+ *Для чего используются ordering и list\_per\_page?* \
  `ordering` задаёт порядок списка по умолчанию. `list_per_page` режет список на страницы в админке и не влияет на пагинацию сайта. На сайте свой `PAGE_SIZE = 5`.
+ *Как настроить отображение связанных объектов с помощью inline?* \
  Inline: класс `TabularInline` или `StackedInline` с `model = Booking`, подключённый в `inlines` родительской админки. Нужен внешний ключ с дочерней модели на родительскую.
+ *Что такое QuerySet и в какой момент ORM-запрос обычно обращается к базе данных?* \
  QuerySet — ленивое описание запроса. SQL обычно выполняется при обходе, срезе, `count()`, `get()`, `exists()`, `aggregate()` или отрисовке шаблона, а не в момент `filter()`.
+ *Чем отличаются методы filter() и exclude()?* \
  `filter` оставляет совпадения. `exclude` убирает совпадения. Оба возвращают QuerySet.
+ *Для чего используется объект Q?* \
  `Q` собирает условия, в том числе OR и NOT: `Q(name__icontains=query) | Q(equipment__icontains=query)` в поиске помещений и `Q(status=...)` внутри `Count`.
+ *Как с помощью ORM отсортировать записи и ограничить выборку?* \
  Сортировка — `order_by("name")` или `order_by("-booking_date")`. Ограничение — срез QuerySet или `LIMIT` пагинатора. Минус задаёт убывание.
+ *Чем отличаются get() и filter() при получении объектов?* \
  `get()` ждёт одну строку и бросает исключение, если строк нет или их несколько. `filter()` возвращает набор и пустой результат исключением не считает.
+ *Для чего используется get\_object\_or\_404() в представлении Django?* \
  `get_object_or_404` вызывает `get` и превращает отсутствие объекта в `Http404`, чтобы представление ответило 404, а не 500.
+ *Чем отличаются select\_related() и prefetch\_related()?* \
  `select_related` делает JOIN для foreign key и one-to-one. `prefetch_related` отдельным запросом забирает наборы: обратную связь и many-to-many. Карточка брони использует первое. Список через `values()` не использует ни то ни другое.
+ *Как с помощью ORM получить поля связанной модели?* \
  Поле связанной модели: `room__name` в фильтре и сортировке, `F("room__name")` в `annotate`, либо `booking.room.name` у уже загруженного объекта.
+ *Почему при работе со связанными объектами может возникать проблема N+1 запросов?* \
  N+1: один запрос за списком и ещё по запросу на каждую строку, когда шаблон трогает связь. Лечится `select_related`, `prefetch_related` или выбором нужных полей через `annotate` и `values`.
+ *Как проверить корректность фильтрации и сортировки в приложении?* \
  Фильтр и сортировку проверяют сменой GET-параметров и сверкой с известными записями, плюс автотестом. SQL в Debug Toolbar показывает, что условие попало в запрос, а не отфильтровалось уже в Python.
+ *Почему отменённые бронирования не должны учитываться при определении занятости помещения и подсчёте активных бронирований?* \
  Отменённая и завершённая бронь — история, а не занятость. Иначе отмена не освобождает комнату, а статистика активных завышается. Поэтому в занятость и в активные счётчики входит только `Status.ACTIVE`.
+ *Почему настройка фильтров в Django Admin не заменяет проверку бизнес-правил?* \
  Фильтр админки лишь помогает найти строки. Он не запрещает сохранить вторую активную бронь и не освобождает комнату на сайте. Правило занятости написано в запросе `active().for_date(...)`.
+ *Какие проверки необходимо выполнить перед фиксацией изменений в Git?* \
  Перед коммитом: `manage.py check`, `makemigrations --check`, тесты, просмотр `git status` и `git diff`. В коммит не кладут `db.sqlite3`, `venv`, пароли и этот файл `ANSWERS_10.md`.
