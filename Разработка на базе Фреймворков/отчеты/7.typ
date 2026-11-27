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
  number: 7,
  teacher: "Ящун Т.В.",
  teacher-position: "доц.",
  student: "Бунто М. В.",
  topic: "ОСНОВЫ БАЗ ДАННЫХ И SQL",
  year: 2026,
)

*Тема проекта:* система бронирования переговорных комнат (Roomly)

*Коммит гит:* 654ba0b

= Цель работы

Изучить основы реляционных баз данных и языка SQL на SQLite: спроектировать таблицы, ключи и типы данных, перенести данные индивидуального проекта из JSON в базу, написать запросы на выборку, фильтрацию, соединение, агрегирование и группировку и получить их результаты в Django-представлениях через модуль `sqlite3`.

= Доработка индивидуального проекта

== Структура базы данных

Сущности предметной области: помещение, пользователь (организатор), бронирование. База — файл `data/roomly.sqlite`, таблицы создаёт `sql/schema.sql`. Первичный ключ каждой таблицы — `id`; в `bookings` внешние ключи `room_id` → `rooms.id` и `user_id` → `users.id`. Дата и время хранятся строками `TEXT`, признак отмены `is_cancelled` — `INTEGER` 0/1.

```sql
CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    capacity INTEGER NOT NULL,
    equipment TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY,
    room_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    booking_date TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    topic TEXT NOT NULL DEFAULT '',
    is_cancelled INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (room_id) REFERENCES rooms (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

== Подключение и перенос данных из JSON

`db/database.py` открывает базу, включает проверку внешних ключей и `sqlite3.Row`:

```python
def get_connection() -> sqlite3.Connection:
    """Открыть базу, включить внешние ключи и имена столбцов.

    Returns:
        Соединение с row_factory = sqlite3.Row.
    """
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection
```

`db/import_json.py` очищает таблицы и вставляет записи методом `executemany()` с параметрами `?`; порядок — помещения, пользователи, бронирования, затем `commit()`:

```python
    connection.executemany(
        """
        INSERT INTO bookings (
            id,
            room_id,
            user_id,
            booking_date,
            start_time,
            end_time,
            topic,
            is_cancelled
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                booking["id"],
                booking["room_id"],
                booking["user_id"],
                booking["booking_date"],
                booking["start_time"],
                booking["end_time"],
                booking["topic"],
                int(booking["is_cancelled"]),
            )
            for booking in bookings
        ],
    )

...
def main() -> None:
    """Очистить таблицы и заново перенести JSON.

    Сначала удаляются бронирования: на них ссылаются внешние ключи.
    """
    connection = get_connection()
    try:
        connection.execute("DELETE FROM bookings")
        connection.execute("DELETE FROM rooms")
        connection.execute("DELETE FROM users")
        import_rooms(connection)
        import_users(connection)
        import_bookings(connection)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
```

Проверка созданных таблиц, ключей и перенесённых данных (чтение `data/roomly.sqlite` из коммита 654ba0b):

```bash
-- Таблицы базы data/roomly.sqlite
name    
--------
bookings
rooms   
users   

-- Внешние ключи bookings (PRAGMA foreign_key_list)
table  from     to
-----  -------  --
users  user_id  id
rooms  room_id  id

-- Перенесённые помещения
id  name                  capacity  equipment                    
--  --------------------  --------  -----------------------------
1   Переговорная «Альфа»  8         проектор, доска, видеосвязь  
2                         4         доска                        
3   Переговорная «Гамма»  12        проектор, видеосвязь, телефон

-- Перенесённые бронирования
id  room_id  user_id  booking_date  topic                       is_cancelled
--  -------  -------  ------------  --------------------------  ------------
1   1        1        2026-09-29    Планёрка отдела разработки  0           
2   1        2        2026-02-23    ПРИМЕР1                     0
```

#shot[структура базы `data/roomly.sqlite` в просмотрщике SQLite (таблицы `rooms`, `users`, `bookings`)]

== SQL-запросы проекта

В `sql/queries.sql` 15 запросов с комментариями: списки (помещения, пользователи, бронирования), `WHERE` (вместимость, активные брони, `LIKE` по оборудованию), `JOIN` (полная информация о брони, все брони с помещением и организатором), подзапрос `NOT IN` (свободные помещения на дату), агрегаты (`COUNT`, `AVG`, `MAX`), `GROUP BY` (по помещениям и организаторам), `HAVING`, `ORDER BY … LIMIT`. Фрагмент:

```sql
-- Полная информация об активном бронировании
SELECT
    bookings.id,
    bookings.booking_date,
    bookings.start_time,
    bookings.end_time,
    bookings.topic,
    rooms.name AS room_name,
    rooms.capacity,
    users.name AS user_name,
    users.email AS user_email
FROM bookings
JOIN rooms
    ON bookings.room_id = rooms.id
JOIN users
    ON bookings.user_id = users.id
WHERE bookings.is_cancelled = 0
ORDER BY bookings.booking_date, bookings.start_time;

...
-- Количество активных бронирований по помещениям
SELECT
    rooms.name AS room_name,
    COUNT(bookings.id) AS bookings_count
FROM rooms
LEFT JOIN bookings
    ON rooms.id = bookings.room_id
    AND bookings.is_cancelled = 0
GROUP BY rooms.id, rooms.name
ORDER BY bookings_count DESC;

-- Количество активных бронирований по организаторам
SELECT
    users.name AS user_name,
    COUNT(bookings.id) AS bookings_count
FROM users
LEFT JOIN bookings
    ON users.id = bookings.user_id
    AND bookings.is_cancelled = 0
GROUP BY users.id, users.name
ORDER BY bookings_count DESC;

-- Помещения, забронированные больше одного раза
SELECT
    rooms.name AS room_name,
    COUNT(bookings.id) AS bookings_count
FROM rooms
JOIN bookings
    ON rooms.id = bookings.room_id
WHERE bookings.is_cancelled = 0
GROUP BY rooms.id, rooms.name
HAVING COUNT(bookings.id) > 1
ORDER BY bookings_count DESC;
```

Результаты части запросов на данных проекта:

```bash
-- Полная информация об активном бронировании (JOIN)
id  booking_date  room_name             user_name  
--  ------------  --------------------  -----------
2   2026-02-23    Переговорная «Альфа»  Михаил     
1   2026-09-29    Переговорная «Альфа»  Иванов И.И.

-- Свободные помещения на 2026-09-29 (WHERE + NOT IN)
id  name                  capacity
--  --------------------  --------
2                         4       
3   Переговорная «Гамма»  12      

-- Сводка по помещениям (COUNT, AVG, MAX)
rooms_count  average_capacity  max_capacity
-----------  ----------------  ------------
3            8.0               12          

-- Активные бронирования по помещениям (GROUP BY)
room_name             bookings_count
--------------------  --------------
Переговорная «Альфа»  2             
                      0             
Переговорная «Гамма»  0             

-- Помещения, забронированные больше одного раза (HAVING)
room_name             bookings_count
--------------------  --------------
Переговорная «Альфа»  2
```

== Получение данных в Django-представлениях

Представления выполняют запросы через `get_connection()` и передают строки `sqlite3.Row` в шаблоны. Пользовательские значения подставляются только параметрами `?`. Поиск свободных помещений по дате (`rooms/views.py`):

```python
def available_rooms(request: HttpRequest) -> HttpResponse:
    """Найти помещения без активного бронирования на дату."""
    booking_date = request.GET.get("date") or ""
    room_list = []
    if booking_date:
        with closing(get_connection()) as connection:
            room_list = connection.execute(
                """
                SELECT
                    rooms.id,
                    rooms.name,
                    rooms.capacity,
                    rooms.equipment
                FROM rooms
                WHERE rooms.id NOT IN (
                    SELECT bookings.room_id
                    FROM bookings
                    WHERE bookings.booking_date = ?
                        AND bookings.is_cancelled = 0
                )
                ORDER BY rooms.name;
                """,
                (booking_date,),
            ).fetchall()
    context = {
        "rooms": room_list,
        "booking_date": booking_date,
    }
    return render(request, "rooms/available.html", context)
```

Страницы, работающие с базой: `/rooms/` — список и отбор по вместимости, `/rooms/available/` — свободные помещения на дату, `/rooms/<id>/` — карточка и доступность на сегодня, `/bookings/` — активные брони с `JOIN`, `/bookings/<id>/` — карточка брони, `/bookings/statistics/` — агрегаты, `GROUP BY` и `HAVING`. В навигацию добавлен пункт «Статистика». README.md дополнен разделом «База данных» и описанием этапа ПР7.

#shot[страница `/rooms/available/?date=2026-09-29` со списком свободных помещений]
#shot[страница `/bookings/statistics/`]

= Результат работы

Созданы таблицы `rooms`, `users`, `bookings` с первичными и внешними ключами, данные из `data/*.json` перенесены в `data/roomly.sqlite`, в `sql/queries.sql` сохранено 15 проверенных запросов всех требуемых видов, представления помещений и бронирований получают данные из SQLite, реализованы поиск свободных помещений и страница статистики. JSON-хранилище и консольная программа сохранены.

= Проверка

#[
  ```bash
  $ python manage.py check
System check identified no issues (0 silenced).
  ```

  ```bash
  $ pytest -v
============================= test session starts ==============================
platform linux -- Python 3.13.5, pytest-9.2.0, pluggy-1.7.0 -- venv/bin/python3
cachedir: .pytest_cache
rootdir: Разработка на базе Фреймворков
configfile: pyproject.toml
testpaths: tests
collecting ... collected 38 items

tests/test_bookings.py::test_is_room_available_empty PASSED              [  2%]
tests/test_bookings.py::test_one_active_booking_per_room_and_date PASSED [  5%]
tests/test_bookings.py::test_create_booking_rejects_bad_interval PASSED  [  7%]
tests/test_bookings.py::test_create_booking_fields PASSED                [ 10%]
tests/test_bookings.py::test_cancel_booking_keeps_object PASSED          [ 13%]
tests/test_bookings.py::test_find_booking_by_id PASSED                   [ 15%]
tests/test_bookings.py::test_get_booking_status PASSED                   [ 18%]
tests/test_bookings.py::test_find_bookings_by_organizer PASSED           [ 21%]
tests/test_bookings.py::test_get_room_schedule PASSED                    [ 23%]
tests/test_models.py::test_room_attributes_and_methods PASSED            [ 26%]
tests/test_models.py::test_room_from_data_and_to_dict PASSED             [ 28%]
tests/test_models.py::test_room_without_equipment PASSED                 [ 31%]
tests/test_models.py::test_user_from_data_and_str PASSED                 [ 34%]
tests/test_models.py::test_booking_links_objects_and_cancel PASSED       [ 36%]
tests/test_rooms.py::test_add_room PASSED                                [ 39%]
tests/test_rooms.py::test_add_room_assigns_next_id PASSED                [ 42%]
tests/test_rooms.py::test_find_room_by_id PASSED                         [ 44%]
tests/test_rooms.py::test_find_room PASSED                               [ 47%]
tests/test_rooms.py::test_check_room_capacity PASSED                     [ 50%]
tests/test_rooms.py::test_filter_rooms_by_equipment PASSED               [ 52%]
tests/test_rooms.py::test_filter_rooms_by_capacity PASSED                [ 55%]
tests/test_rooms.py::test_sort_rooms PASSED                              [ 57%]
tests/test_storage.py::test_rooms_roundtrip_keeps_id PASSED              [ 60%]
tests/test_storage.py::test_users_roundtrip PASSED                       [ 63%]
tests/test_storage.py::test_load_missing_files PASSED                    [ 65%]
tests/test_storage.py::test_load_broken_json PASSED                      [ 68%]
tests/test_storage.py::test_load_wrong_shape PASSED                      [ 71%]
tests/test_storage.py::test_bookings_roundtrip_links_objects PASSED      [ 73%]
tests/test_storage.py::test_load_bookings_skips_missing_links PASSED     [ 76%]
tests/test_users.py::test_add_user PASSED                                [ 78%]
tests/test_users.py::test_find_user_by_name PASSED                       [ 81%]
tests/test_users.py::test_find_users_by_substring PASSED                 [ 84%]
tests/test_web.py::test_index_has_navigation PASSED                      [ 86%]
tests/test_web.py::test_room_list_and_detail PASSED                      [ 89%]
tests/test_web.py::test_booking_list_and_detail PASSED                   [ 92%]
tests/test_web.py::test_available_rooms_by_date PASSED                   [ 94%]
tests/test_web.py::test_statistics_page PASSED                           [ 97%]
tests/test_web.py::test_unknown_url_uses_custom_404 PASSED               [100%]

============================== 38 passed in 0.07s ==============================
  ```

  ```bash
  $ flake8 . --extend-exclude=venv
  ```
]

= Git

Коммит `654ba0b` — «PR7: перенос данных в SQLite и SQL-запросы».

= Вывод

В результате выполнения ПР7 индивидуальный проект получил слой реляционного хранения данных: базу SQLite, набор SQL-запросов и получение данных в Django-представлениях через `sqlite3`. Это подготавливает переход к Django ORM в ПР9.

= Ответы на контрольные вопросы

+ *Что такое база данных?* \
  Организованный набор взаимосвязанных данных, которые хранятся по определённой структуре и доступны для поиска и изменения.
+ *Чем база данных отличается от СУБД?* \
  База данных — сами данные. СУБД — программа, которая их хранит, выполняет запросы, следит за целостностью. В проекте СУБД — SQLite, база — файл `data/roomly.sqlite`.
+ *Что такое реляционная база данных?* \
  База, где данные лежат в таблицах, а связи между таблицами задаются значениями ключей.
+ *Что такое таблица, запись и поле?* \
  Таблица описывает одну сущность (`rooms`), запись — одна строка (одно помещение), поле — один столбец (`capacity`).
+ *Какие типы данных поддерживает SQLite?* \
  Классы хранения `NULL`, `INTEGER`, `REAL`, `TEXT`, `BLOB`. Отдельного типа даты и логического типа нет: дата хранится как `TEXT` в формате `YYYY-MM-DD`, признак отмены — `INTEGER` 0/1.
+ *Для чего используется первичный ключ?* \
  Однозначно определяет запись. В проекте у всех таблиц `id INTEGER PRIMARY KEY`.
+ *Для чего используется внешний ключ?* \
  Ссылается на первичный ключ другой таблицы и не даёт сослаться на несуществующую запись. В `bookings` это `room_id` → `rooms.id` и `user_id` → `users.id`.
+ *Что такое SQL?* \
  Декларативный язык запросов к реляционным базам: создание таблиц, выборка, вставка, изменение и удаление данных.
+ *Чем SQL-запрос отличается от Python-кода?* \
  SQL описывает, какой результат нужен, а не как его получить; выполняет его СУБД. Python-код задаёт последовательность действий и выполняется интерпретатором.
+ *Для чего используются SELECT и FROM?* \
  `SELECT` перечисляет нужные столбцы или выражения, `FROM` — таблицу, из которой они берутся.
+ *Для чего используется WHERE?* \
  Оставляет только строки, удовлетворяющие условию, например `WHERE capacity >= 8`.
+ *Чем отличаются операторы =, \<\> и !=?* \
  `=` — равно. `<>` и `!=` — не равно; `<>` из стандарта SQL, `!=` SQLite тоже понимает.
+ *Для чего используются IN, BETWEEN и LIKE?* \
  `IN` — значение из списка или подзапроса (`NOT IN` в поиске свободных помещений), `BETWEEN` — диапазон включительно, `LIKE` — шаблон строки (`equipment LIKE '%проектор%'`).
+ *Как используются AND, OR и NOT?* \
  Объединяют условия: `AND` — оба истинны, `OR` — хотя бы одно, `NOT` — отрицание. Пример: `booking_date = ? AND is_cancelled = 0`.
+ *Как в SQL проверяется значение NULL?* \
  Только `IS NULL` / `IS NOT NULL`: сравнение `= NULL` всегда даёт неизвестный результат.
+ *Для чего используется DISTINCT?* \
  Убирает повторяющиеся строки из результата.
+ *Для чего используется ORDER BY?* \
  Сортирует результат, например `ORDER BY booking_date, start_time`.
+ *Чем отличаются ASC и DESC?* \
  `ASC` — по возрастанию (по умолчанию), `DESC` — по убыванию.
+ *Для чего используются LIMIT и OFFSET?* \
  `LIMIT` ограничивает число строк, `OFFSET` пропускает первые строки. В проекте — две самые вместительные переговорные: `ORDER BY capacity DESC LIMIT 2`.
+ *Почему LIMIT и OFFSET рекомендуется использовать вместе с ORDER BY?* \
  Без `ORDER BY` порядок строк не гарантирован, и «первые N» или «следующая страница» могут меняться от запуска к запуску.
+ *Что такое агрегатная функция?* \
  Функция, которая считает одно значение по набору строк: `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`.
+ *Чем отличаются COUNT(\*) и COUNT(column)?* \
  `COUNT(*)` считает все строки, `COUNT(column)` — только строки, где столбец не `NULL`. Поэтому в статистике по помещениям с `LEFT JOIN` используется `COUNT(bookings.id)`: помещение без броней даёт 0.
+ *Для чего используются MIN, MAX, AVG и SUM?* \
  Минимум, максимум, среднее и сумма по столбцу. В сводке по помещениям — `AVG(capacity)` и `MAX(capacity)`.
+ *Для чего используется GROUP BY?* \
  Делит строки на группы с одинаковым значением и считает агрегат для каждой группы — число активных броней по помещениям и по организаторам.
+ *Чем WHERE отличается от HAVING?* \
  `WHERE` фильтрует строки до группировки, `HAVING` — группы после неё, по значению агрегата: `HAVING COUNT(bookings.id) > 1`.
+ *В каком порядке выполняются основные части SQL-запроса?* \
  `FROM`/`JOIN` → `WHERE` → `GROUP BY` → `HAVING` → `SELECT` → `ORDER BY` → `LIMIT`/`OFFSET`.
+ *Для чего используется модуль sqlite3?* \
  Модуль стандартной библиотеки Python для работы с SQLite: подключение, выполнение SQL, получение результатов, транзакции.
+ *Какие основные этапы работы с SQLite из Python?* \
  `sqlite3.connect()` → (`PRAGMA foreign_keys = ON`) → `execute()`/`executemany()` → `fetchone()`/`fetchall()` → `commit()` при изменениях → `close()`.
+ *Для чего используется cursor?* \
  Курсор выполняет запросы и хранит позицию в результате выборки. `connection.execute()` создаёт его неявно.
+ *Для чего используется commit()?* \
  Фиксирует транзакцию. Без `commit()` вставки и удаления не попадут в файл базы. В `db/import_json.py` при ошибке выполняется `rollback()`.
+ *Почему нельзя подставлять значения пользователей в SQL через f-строки?* \
  Из-за SQL-инъекций: введённый текст становится частью запроса и может изменить его смысл. Кроме того, ломается экранирование кавычек.
+ *Что такое параметризованный SQL-запрос?* \
  Запрос с местами `?`, значения передаются отдельно: `execute("... WHERE id = ?", (room_id,))`. Драйвер сам подставляет их безопасно.
+ *Для чего используется executemany()?* \
  Выполняет один запрос для списка наборов параметров. В `db/import_json.py` так вставляются все помещения, пользователи и бронирования.
+ *Чем файловая SQLite-база отличается от базы :memory:?* \
  Файловая база хранится на диске и переживает перезапуск. `:memory:` живёт в оперативной памяти и исчезает при закрытии соединения.
+ *В каких случаях база :memory: удобна?* \
  Для тестов и экспериментов: быстро, не оставляет файлов, каждый запуск начинается с чистой базы.
+ *Как получить результаты SELECT в Python?* \
  `fetchone()` — одна строка, `fetchall()` — список строк, либо итерация по курсору. С `row_factory = sqlite3.Row` к полям обращаются по имени: `row["name"]`, а в шаблоне `room.name`.
+ *Какие операции с данными уже выполнялись в проекте до перехода на базу данных?* \
  Просмотр и поиск помещений, проверка доступности на дату, создание и отмена бронирования, расписание помещения, поиск броней по организатору. Данные хранились в JSON (`storage.py`).
+ *Какие преимущества даёт хранение данных в базе по сравнению с JSON-файлами?* \
  Типы и ограничения на уровне базы, внешние ключи, выборка и подсчёт запросом без загрузки всего файла в память, транзакции, одновременный доступ.
+ *Какие таблицы и связи используются в собственной предметной области?* \
  `rooms`, `users`, `bookings`. `bookings` связана с `rooms` и `users` через `room_id` и `user_id` (связи «многие к одному»).
+ *Какие SQL-запросы необходимы для решения основных задач собственного проекта?* \
  Список помещений и отбор по вместимости, активные бронирования с названием помещения и организатором (`JOIN`), свободные помещения на дату, число броней и сводка по помещениям, группировка по помещениям и организаторам, отбор групп через `HAVING`.
