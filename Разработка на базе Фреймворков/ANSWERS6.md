# Ответы по шаблонам и страницам Roomly

Страницы отдаёт Django: `render()`, шаблоны `.html`, `{% extends %}`, `{% include %}`, `{% url %}` и статика. Ниже для каждого пункта: где это лежит, как работает и какое изменение показать на защите.

Сервер для показа: `python manage.py runserver`. В `roomly/settings.py` стоит `DEBUG = True`.

## 1. Наследование шаблонов

Базовый шаблон — `templates/base.html`. В нём каркас документа: `<html>`, Bootstrap, свой CSS, логотип, навигация, `<main>`, подвал и скрипт. Заголовок вкладки по умолчанию — `Roomly`:

```html
<title>{% block title %}Roomly{% endblock %}</title>
```

Дочерний шаблон, например `homepage/templates/homepage/index.html`, начинается с `{% extends "base.html" %}`. Так же устроены `rooms/room_list.html`, `rooms/room_detail.html`, `bookings/booking_list.html`, `bookings/booking_detail.html` и обе страницы 404.

`{% extends "base.html" %}` значит: взять базовый файл целиком и подставить только те `{% block %}`, которые дочерний шаблон переопределил. Навигация, подвал и подключение CSS остаются из базы.

Показ. В `index.html` замени `{% block title %}Главная{% endblock %}` на `Roomly — главная` и обнови `/`. Текст вкладки станет «Roomly — главная». Надпись «Roomly» у логотипа не изменится: её рисует `base.html`, вне блока `title`. Верни «Главная».

## 2. Переопределение блоков

В базе два блока. `title` попадает в `<title>`. `content` попадает в `<main>` и по умолчанию пустой:

```html
<main class="container pb-5">
    {% block content %}{% endblock %}
</main>
```

Дочерняя страница переопределяет оба. Навигацию не переопределяет никто: она в базе через `{% include "includes/navigation.html" %}`.

Показ. В `rooms/templates/rooms/room_list.html` замени текст заголовка `Помещения` на `Список комнат` и открой `/rooms/`. В `<main>` будет новый заголовок, меню сверху останется. На `/` и `/bookings/` останется их собственный `content`, потому что у каждой страницы свой шаблон. Движок при `render()` собирает базу и дочерний файл в один HTML и отдаёт его в ответе. Верни прежний заголовок.

## 3. Передача контекста

Вызов `render()` в `rooms/views.py`:

```python
def rooms(request: HttpRequest) -> HttpResponse:
    """Показать список всех помещений."""
    room_list, _, _ = load_catalog()
    context = {"rooms": room_list}
    return render(request, "rooms/room_list.html", context)
```

`load_catalog()` в `homepage/catalog.py` читает `data/rooms.json`, `data/users.json` и `data/bookings.json`. В шаблоне ключ словаря становится именем переменной: `{{ rooms|length }}` и `{% for room in rooms %}`.

В карточке комнаты контекст шире:

```python
context = {
    "room": room,
    "today": today,
    "available": available,
    "status": get_booking_status(available),
}
return render(request, "rooms/room_detail.html", context)
```

Шаблон `rooms/room_detail.html` читает `room`, `today`, `available` и `status`.

Показ. В `rooms()` переименуй ключ `"rooms"` в `"room_items"`, шаблон не трогай, обнови `/rooms/`. Страница откроется с кодом 200, но `{{ rooms|length }}` будет пустым, а цикл уйдёт в ветку «Помещений пока нет.». Имя в словаре и имя в шаблоне сравниваются буквально. Старый ключ `rooms` в контексте больше нет, поэтому прежняя переменная ничего не находит. Верни ключ `"rooms"`.

## 4. Обращение к атрибутам объектов

Объекты предметной области лежат в `models/rooms.py`, `models/bookings.py` и `models/users.py`. Это обычные классы, не модели Django ORM.

| Объект | Атрибуты в шаблоне | Где |
| --- | --- | --- |
| `Room` | `id`, `name`, `capacity`, `equipment` | `room_card.html`, `room_detail.html` |
| `Booking` | `id`, `topic`, `booking_date`, `start_time`, `end_time`, `is_cancelled` | список и карточка бронирования |
| вложенные | `booking.room.name`, `booking.room.id`, `booking.user.name`, `booking.user.email` | `booking_list.html`, `booking_detail.html` |

На `/rooms/1/` выводятся `{{ room.name }}` («Переговорная «Альфа»») и `{{ room.capacity }}` (8). На `/bookings/1/` — `{{ booking.topic }}` и `{{ booking.user.email }}`.

Движок для `{{ room.name }}` ищет по порядку ключ словаря, атрибут, затем индекс. Точка в шаблоне — это этот поиск, а не вызов метода Python.

Показ. В `room_detail.html` замени `room.name` на `room.title` и обнови `/rooms/1/`. У `Room` есть `name`, атрибута `title` нет. Django не поднимает `AttributeError` наружу: обращение равносильно отсутствующей переменной, в HTML попадает пустая строка, код ответа остаётся 200. Заголовок просто пропадает. Верни `room.name`.

## 5. Обработка отсутствующих переменных

Показ. В блок `content` файла `homepage/index.html` добавь `{{ missing_value }}` и открой `/`. Такой переменной нет в контексте `index()`: представление вызывает `render()` без словаря. Страница останется целой, код 200, на месте выражения пусто.

При разборе `{{ missing_value }}` движок ищет имя в контексте, не находит и подставляет настройку `string_if_invalid`. По умолчанию это `""`. Исключение `VariableDoesNotExist` перехватывается внутри движка. Опечатку не видно ни по коду ответа, ни по падению сервера. Искать её приходится сравнением ключей `render()` и имён в шаблоне. Для отладки в `TEMPLATES["OPTIONS"]` можно задать непустой `string_if_invalid`, например `"ОШИБКА: %s"`. Убери вставку после показа.

## 6. Автоматическое экранирование HTML

Любое `{{ ... }}` экранируется само. Отдельного `html.escape` в шаблонах нет. Так выводятся название комнаты, оборудование, тема, имя, почта и `{{ message }}` на странице 404. Разметка шаблона (`<h1>`, `class=...`) в экранирование не попадает: это доверенный HTML файла.

Показ. В `data/rooms.json` у комнаты 1 временно задай имя `Переговорная <b>Альфа</b><script>alert(1)</script>`. Открой `/rooms/1/`. Теги видны как текст, скрипт не выполняется: `<` превратился в `&lt;`. Затем в этой одной подстановке напиши `{{ room.name|safe }}`. Слово «Альфа» станет жирным, браузер попытается выполнить скрипт. Верни имя в JSON и убери `|safe`.

Экранирование отключают фильтром `|safe`, функцией `mark_safe` и блоком `{% autoescape off %}`. Для данных из JSON и от пользователя это опасно: тема встречи и имя организатора. Если в них окажется `<script>` или `<img onerror=...>`, браузер выполнит это в контексте сайта. Так возникает XSS. Экранирование оставляют включённым для любого текста, который сайт не собрал сам как готовую разметку.

## 7. Обработка коллекций

Список комнат — цикл в `rooms/templates/rooms/room_list.html`:

```django
<div class="list-group">
    {% for room in rooms %}
        {% include "rooms/includes/room_card.html" %}
    {% empty %}
        <p class="lead">Помещений пока нет.</p>
    {% endfor %}
</div>
```

Список бронирований устроен так же в `bookings/booking_list.html`: `{% for booking in bookings %}` и ветка «Бронирований пока нет.».

Показ. В начале `rooms()` после загрузки подставь `room_list = []` и открой `/rooms/`. Заголовок останется, карточки исчезнут, появится «Помещений пока нет.». Убери подмену — снова комнаты из `data/rooms.json`.

Ветка `{% empty %}` срабатывает, когда коллекция пустая. Без неё цикл не выводит ни одной итерации, и под заголовком остаётся пустое место.

## 8. Условное отображение

Статус бронирования — `bookings/templates/bookings/includes/booking_status.html`:

```django
{% if booking.is_cancelled %}
<span class="badge bg-secondary booking-status">Отменено</span>
{% else %}
<span class="badge bg-success booking-status">Активно</span>
{% endif %}
```

Фрагмент подключают и список `/bookings/`, и карточка `/bookings/1/`. Отдельное условие в `room_detail.html`: `{% if available %}` выбирает зелёный или красный значок для текста из `get_booking_status()` — «Переговорная свободна» или «Переговорная уже занята».

Показ. В `data/bookings.json` у записи `"id": 1` поставь `"is_cancelled": true`. Обнови `/bookings/` и `/bookings/1/`. Значок №1 сменится с зелёного «Активно» на серый «Отменено». Верни `false`.

Второй вариант: в шаблоне замени условие на `{% if not booking.is_cancelled %}`. У активных записей появится «Отменено» при тех же данных. Верни условие.

## 9. Использование фильтров

Фильтр стоит после значения через `|`. Он берёт значение, возвращает новое для вывода и не меняет объект в контексте. Цепочка читается слева направо.

Уже стоят такие фильтры:

- `{{ rooms|length }}` и `{{ bookings|length }}` — число элементов;
- `{{ room.name|default:"Без названия" }}` — запасной текст для пустого имени;
- `{{ booking.topic|default:"Без темы" }}` — то же для темы.

Показ. К уже существующему выражению в `room_card.html` добавь второй фильтр:

```django
{{ room.name|default:"Без названия"|upper }}
```

Открой `/rooms/`. Подписи станут «ПЕРЕГОВОРНАЯ «АЛЬФА»» и так далее. В JSON имя не меняется: преобразовано только выводимое значение. `default` отрабатывает первым, `upper` — уже по результату. Убери `|upper`.

## 10. Обработка пустых значений

Фильтр `default` уже используется. В карточке комнаты заголовок такой:

```django
<h1 class="display-4">{{ room.name|default:"Без названия" }}</h1>
```

То же выражение есть в `room_card.html` и для `booking.room.name`. Тема — `{{ booking.topic|default:"Без темы" }}`.

`|default:"Без названия"` подставляет запасной текст, когда значение пустое: `None`, `""`, пустой список, отсутствующая переменная. `|default_if_none` реагирует только на `None` и пустую строку оставляет как есть. Фильтр нужен, чтобы на месте незаполненного поля оставалась понятная подпись.

Пустое оборудование обработано условием, а не `default`. В `room_card.html` и в карточке: если `room.equipment` ложно, выводится слово «нет».

Показ. У «Беты» в `data/rooms.json` временно запиши `"name": ""`. Открой `/rooms/` и `/rooms/2/`. Вместо пустого заголовка будет «Без названия». Верни «Переговорная «Бета»». Для оборудования запиши `"equipment": []` и открой те же адреса: на месте списка будет «нет». Верни `["доска"]`.

## 11. Повторное использование шаблонов

`{% include %}` вставляет другой шаблон в месте тега. Общие фрагменты:

- `templates/includes/navigation.html` — из `base.html`, поэтому меню есть на каждой странице;
- `rooms/templates/rooms/includes/room_card.html` — из списка комнат, один раз на комнату;
- `bookings/templates/bookings/includes/booking_status.html` — из списка и из карточки бронирования.

Показ. В `booking_status.html` замени текст `Активно` на `Подтверждено`. Обнови `/bookings/` и `/bookings/1/`. Новая подпись появится на обеих страницах, потому что обе включают один файл. Правка только в `booking_detail.html` список не затронет. Верни «Активно».

## 12. Передача данных во включаемый шаблон

Карточка комнаты читает переменную `room` из контекста родителя. Отдельного `with` нет, поэтому во фрагмент попадает весь контекст списка:

```django
<a class="list-group-item list-group-item-action room-card" href="{% url 'rooms:detail' room.id %}">
    <strong>{{ room.name|default:"Без названия" }}</strong>
    <span class="badge bg-secondary">{{ room.capacity }} мест</span>
```

Значок бронирования так же читает `booking` и `booking.is_cancelled`. Представление передаёт коллекцию, цикл даёт текущий элемент, `include` видит его под тем же именем.

Показ. В `room_list.html` замени включение на:

```django
{% include "rooms/includes/room_card.html" with item=room only %}
```

Фрагмент по-прежнему читает `room`. Из-за `only` родительский контекст внутрь не попадает, имени `room` во фрагменте нет, название и вместимость пропадают, ссылка собирается без идентификатора. Имя в `with` и имя внутри фрагмента должны совпадать. Верни прежний `{% include %}` без `with`.

## 13. Формирование динамических URL

Ссылки собирает тег `{% url %}`. Он вызывает тот же механизм, что `reverse()`:

- карточка комнаты: `{% url 'rooms:detail' room.id %}` → `/rooms/1/`, `/rooms/2/`, `/rooms/3/`;
- список бронирований: `{% url 'bookings:detail' booking.id %}` → `/bookings/1/`;
- из карточки бронирования на комнату: `{% url 'rooms:detail' booking.room.id %}`.

Имя маршрута берётся из `name=` в `rooms/urls.py` и `bookings/urls.py`. Префикс `/rooms/` добавляет `path("rooms/", include("rooms.urls"))` в `roomly/urls.py`.

Показ. В `room_card.html` замени `room.id` на число `1`. Открой `/rooms/` и посмотри адреса «Беты» и «Гаммы». У всех трёх ссылок будет `/rooms/1/`. Верни `room.id` — у «Беты» снова `/rooms/2/`, у «Гаммы» `/rooms/3/`. Идентификатор в `{% url %}` становится куском пути.

## 14. Работа с пространствами имён

Пространство имён объявлено в каждом файле маршрутов через `app_name`:

- `homepage/urls.py` — `app_name = "homepage"`, маршрут `name="index"`;
- `rooms/urls.py` — `app_name = "rooms"`, маршруты `list` и `detail`;
- `bookings/urls.py` — `app_name = "bookings"`, маршруты `bookings` и `detail`.

В `roomly/urls.py` приложения подключены через `include` без второго аргумента. Пространство берётся из `app_name`. В шаблонах имена квалифицированные: `homepage:index`, `rooms:list`, `rooms:detail`, `bookings:bookings`, `bookings:detail`. В `rooms/views.py` и `bookings/views.py` строки `"rooms:list"` и `"bookings:bookings"` передаются в шаблон 404 и подставляются в `{% url back_url_name %}`.

Показ. В `rooms/urls.py` замени `app_name = "rooms"` на `app_name = "meeting_rooms"` и открой `/rooms/`. Страница упадёт с `NoReverseMatch`: шаблон всё ещё ищет `rooms:detail` и `rooms:list`. Согласованно придётся обновить:

- `templates/includes/navigation.html` — `rooms:list`;
- `homepage/templates/homepage/index.html` — `rooms:list`;
- `rooms/templates/rooms/includes/room_card.html` — `rooms:detail`;
- `rooms/templates/rooms/room_detail.html` — `rooms:list`;
- `bookings/templates/bookings/booking_detail.html` — `rooms:detail`;
- `rooms/views.py` — аргумент `"rooms:list"` в `http_not_found`.

Если менять не `app_name`, а `name="detail"` на `name="card"`, список тот же по всем `{% url 'rooms:detail' ... %}`. Тесты в `tests/test_web.py` ходят по готовым путям `client.get("/rooms/1/")` и от переименования `name` не ломаются. Ломается сборка ссылок. После показа верни `app_name = "rooms"`.

## 15. Преобразование параметров маршрута

Числовые конвертеры стоят в маршрутах:

```python
# rooms/urls.py
urlpatterns = [
    path("", views.rooms, name="list"),
    path("<int:room_id>/", views.room_detail, name="detail"),
]
```

```python
# bookings/urls.py
urlpatterns = [
    path("", views.bookings, name="bookings"),
    path("<int:booking_id>/", views.booking_detail, name="detail"),
]
```

Показ. Открой `/rooms/abc/` и `/bookings/abc/`. Представление `room_detail` не вызывается. Конвертер `int` совпадает только с цифрами, строка `abc` образцу не подходит, маршрут не выбран. При `DEBUG = True` Django показывает техническую 404: путь не совпал ни с одним маршрутом. Параметр в функцию не передаётся, до `int("abc")` внутри представления дело не доходит. Запрос `/rooms/1/` приходит в `room_detail` уже с `room_id` типа `int` и значением `1`.

## 16. Обработка отсутствующих объектов

Поиск по идентификатору:

- комната — `find_room_by_id()` в `domain/rooms.py`, при промахе `None`;
- бронирование — `find_booking_by_id()` в `domain/bookings.py`, так же `None`.

Оба представления проверяют результат до обращения к полям. Промах уходит в `http_not_found()` из `homepage/views.py`. Та вызывает `render(..., "homepage/object_not_found.html", context, status=404)`.

```python
room = find_room_by_id(room_list, room_id)
if room is None:
    return http_not_found(
        request,
        "Помещение не найдено.",
        "rooms:list",
        "К списку помещений",
    )
```

Для бронирования текст другой: «Бронирование не найдено.», ссылка назад — `bookings:bookings`. Метода `get_object_or_404` нет: объекты читаются из JSON, не из базы Django.

Показ. Открой `/rooms/999/` и `/bookings/999/`. Код ответа 404, на странице соответствующая фраза и кнопка возврата. Это работает и при `DEBUG = True`, потому что статус выставляет само представление, исключение `Http404` не бросается. Проверка уже есть в `tests/test_web.py`. Если ветку `if room is None` убрать, следующая строка `room.id` даст `AttributeError` и ответ 500. Именно эта ветка превращает промах поиска в 404.

## 17. Различие ошибок маршрутизации и поиска объекта

Два запроса дают статус 404 на разных этапах.

Несуществующий маршрут, например `/no-such-page/`. Сопоставление в `roomly/urls.py` и во вложенных `urlpatterns` заканчивается ничем. Исключение возникает в резолвере, до представления. При `DEBUG = True` браузер показывает техническую страницу Django со списком маршрутов. Обработчик `handler404 = "homepage.views.page_not_found"` при включённой отладке для такого промаха не вызывается. При `DEBUG = False` сработает `page_not_found`: шаблон `homepage/page_not_found.html`, заголовок «Страница не найдена», фраза «Запрошенный адрес не существует.», статус 404. Это покрывает тест `test_unknown_url_uses_custom_404`.

Существующий маршрут и отсутствующий объект, `/rooms/999/`. Образец `rooms/<int:room_id>/` совпал, в `room_detail` пришло `room_id=999`. Ошибка возникает уже в представлении, когда `find_room_by_id` вернул `None`. Ответ — каркас сайта и текст «Помещение не найдено.», статус 404, в том числе при `DEBUG = True`.

Показ. Открой оба адреса рядом. У первого на отладочной странице написано, что путь не совпал ни с одним маршрутом. У второго обычная страница Roomly с текстом про помещение. После успешного маршрута запрос живёт дальше, и представление само решает, какой статус вернуть.

## 18. Обработка ошибок поиска шаблона

Представление называет файл в `render()`. Для карточки комнаты это строка `"rooms/room_detail.html"` в `rooms/views.py`. Загрузчик ищет файл в `DIRS` (`templates/` проекта) и в каталогах приложений, потому что `APP_DIRS = True`.

Неверное имя файла, например `"rooms/room_detal.html"`, при существующем `room_detail.html`. Файла нет — исключение `TemplateDoesNotExist`. Страница отладки перечисляет имя шаблона и пути, где его искали. До выполнения тегов дело не доходит.

Файл найден, внутри синтаксическая ошибка: незакрытый `{% if %}`, лишний `{% endif %}`, опечатка в имени тега. Это `TemplateSyntaxError`. Страница отладки показывает файл, номер строки и текст вроде unclosed tag. Представление и контекст при этом уже ни при чём: шаблон не разобран.

Код ответа в обоих случаях при `DEBUG = True` — жёлтая отладочная страница. Различие в типе исключения и в том, есть ли в сообщении строка внутри найденного файла. После показа верни правильное имя файла.

## 19. Поиск ошибок в шаблонах

Разбор на живом шаблоне — цикл в `room_list.html`: `{% for room in rooms %}`, внутри `{% include %}`, затем `{% empty %}` и `{% endfor %}`. Парные теги есть и в `booking_status.html`: `{% if %}` закрыт `{% endif %}`.

Показ. Временно удали `{% endfor %}` в `room_list.html` и открой `/rooms/`. Движок выбросит `TemplateSyntaxError` на этапе разбора. HTML пользователю не отправится: страница не формируется, пока шаблон не станет синтаксически целым. Верни `{% endfor %}`. Список комнат снова отдаёт 200. Ошибка мешала ответу, потому что шаблон компилируется до подстановки данных. Пока конструкция не закрыта, `render()` не может собрать документ.

Незакрытый HTML-тег, например забытый `</div>`, ведёт себя иначе: шаблонный синтаксис цел, ответ уходит с кодом 200, а в браузере «едет» вёрстка. Это видно в инспекторе, а не на жёлтой странице Django.

## 20. Подключение статических ресурсов

В `base.html` первой строкой стоит `{% load static %}`. Без этой загрузки тег `{% static %}` недоступен. Дальше три ресурса:

- CSS: `{% static 'homepage/css/style.css' %}`;
- логотип: `{% static 'homepage/img/logo.png' %}`;
- JavaScript: `{% static 'homepage/js/main.js' %}`.

Файлы лежат в `homepage/static/homepage/css/style.css`, `homepage/static/homepage/img/logo.png` и `homepage/static/homepage/js/main.js`. Приложение `django.contrib.staticfiles` подключено, `STATIC_URL = "static/"`. Тег подставляет этот префикс, в браузере адрес выглядит как `/static/homepage/css/style.css`. Сверху ещё подключён Bootstrap с CDN, это отдельный `<link>`, не `{% static %}`.

Показ. Замени путь CSS на `homepage/css/missing.css` и обнови `/` с открытыми инструментами разработчика, вкладка Network. Запрос к CSS завершится с 404. Скругление карточек и серый подвал пропадут, Bootstrap останется. В исходнике страницы атрибут `href` у `<link>` совпадёт с ошибочным адресом. Значит, сбой связан с адресом файла. Верни прежний путь: запрос снова 200.

Если файл открывается с кодом 200, а блок всё равно выглядит обычно, причину ищут в имени класса, а не в пути.

## 21. Изменение стилей страницы

Свой файл — `homepage/static/homepage/css/style.css`. Карточка комнаты в HTML имеет класс `room-card` (`room_card.html` и `room_detail.html`). В CSS ему соответствует селектор `.room-card` с `border-radius: 0.5rem`. Класс `booking-status` на значке статуса соответствует правилу `.booking-status`. Класс `roomly-logo` задаёт размер логотипа, `roomly-footer` — цвет подвала.

Связка прямая: браузер берёт значение атрибута `class` и ищет в загруженных таблицах селектор с тем же именем. Классы Bootstrap (`navbar`, `bg-light`, `bg-success`, `list-group-item`) работают так же, только правило лежит в CSS с CDN.

Показ. В `style.css` замени у `.room-card` значение `border-radius` с `0.5rem` на `1.5rem`. Обнови `/rooms/` и `/rooms/1/`. Углы карточек станут заметно круглее. Если написать класс `room-card-xl`, которого в CSS нет, вид не изменится: селектора с таким именем в подключённой таблице нет. Верни `0.5rem`. Жёсткое обновление страницы нужно, если браузер держит старый CSS.

## 22. Диагностика подключения JavaScript

Скрипт подключён в конце `base.html`:

```html
<script src="{% static 'homepage/js/main.js' %}"></script>
```

Файл `homepage/static/homepage/js/main.js` по `DOMContentLoaded` находит элемент `<span id="current-year">` в подвале и записывает в него текущий год. Пока скрипт не отработал, в подвале пустое место после слова «Roomly,».

Две поломки смотрят во вкладках Network и Console.

Файл не загрузился. Запрос к `/static/homepage/js/main.js` или к ошибочному `src` даёт 404. В Console есть сообщение о неудачной загрузке ресурса. Функции из этого файла не существуют. Год в подвале остаётся пустым.

Файл загрузился, ошибка внутри. Запрос со статусом 200, во вкладке Network виден размер ответа. В Console — `ReferenceError`, `TypeError` или другая ошибка со ссылкой на строку `main.js`. Код выполнился до этой строки. `console.log` в первой строке файла появляется в Console только в этом случае.

Показ. Временно испорти путь скрипта так же, как путь CSS в пункте 20. Год пропадёт, в Network будет 404. Верни путь. Затем в `main.js` после получения узла обратись к несуществующему имени и обнови страницу: Network покажет 200, Console покажет ошибку со строкой файла. Верни скрипт.

## 23. Организация шаблонов приложений

Приложения три: `homepage`, `rooms`, `bookings`. У каждого свой каталог шаблонов, и внутри ещё каталог с именем приложения:

- `homepage/templates/homepage/index.html`, `page_not_found.html`, `object_not_found.html`;
- `rooms/templates/rooms/room_list.html`, `room_detail.html`, `includes/room_card.html`;
- `bookings/templates/bookings/booking_list.html`, `booking_detail.html`, `includes/booking_status.html`.

Общий каркас вынесен в каталог проекта, его Django ищет через `DIRS`: `BASE_DIR / "templates"`. Там `base.html` и `includes/navigation.html`.

Путь в `render()` повторяет хвост после `templates/`: `"rooms/room_detail.html"`, `"bookings/booking_detail.html"`, `"homepage/index.html"`.

`APP_DIRS = True`, порядок приложений в `INSTALLED_APPS` — `homepage`, `rooms`, `bookings`. Загрузчик при коротком имени берёт первый найденный файл. Если оба приложения заведут `detail.html` прямо в `templates/`, шаблон одного молча перекроет шаблон другого. Вложенный каталог делает имя уникальным: `rooms/room_detail.html` не совпадёт с `bookings/booking_detail.html`. Каталог `templates/` проекта нужен для файлов, которые не принадлежат одному приложению.

## 24. Согласованность представления и шаблона

Для `/rooms/1/` представление кладёт объект в контекст под ключом `room`, шаблон читает его атрибуты: `room.name`, `room.capacity`, `room.equipment`. Рядом передаются `today`, `available` и `status`, и шаблон использует те же имена.

Показ поломки. В `room_detail()` переименуй ключ `"room"` в `"item"`, шаблон не меняй. Обнови `/rooms/1/`. Код ответа 200, заголовок пустой: шаблон по-прежнему ищет `room`, а в контексте лежит `item`. Исправь согласованно: либо верни ключ `"room"`, либо в шаблоне замени `room` на `item` во всех обращениях, включая `{% url 'rooms:detail' room.id %}`. После правки обоих концов снова видны «Переговорная «Альфа»», вместимость 8 и оборудование. На защите достаточно вернуть ключ `"room"`.

Та же связка у бронирования: представление передаёт `{"booking": booking}`, шаблоны читают `booking.id`, `booking.topic`, `booking.user`, `booking.room`.

## 25. Путь обработки HTTP-запроса

Запрос `GET /rooms/1/` проходит так.

1. Корневой конфиг `ROOT_URLCONF = "roomly.urls"`. В `roomly/urls.py` префикс `rooms/` совпадает с `path("rooms/", include("rooms.urls"))`. Дальше резолвер ищет образец для хвоста `1/`.
2. В `rooms/urls.py` пространство имён `rooms`, образец `<int:room_id>/` совпадает с именем `detail`. Конвертер превращает текст `"1"` в целое `1` и вызывает `rooms.views.room_detail(request, room_id=1)`.
3. Представление вызывает `load_catalog()` в `homepage/catalog.py`. Та читает `data/rooms.json`, `data/users.json` и `data/bookings.json` через `storage.py` и собирает объекты `Room`, `User`, `Booking`.
4. `find_room_by_id(room_list, 1)` возвращает комнату id=1: имя «Переговорная «Альфа»», вместимость 8, оборудование «проектор», «доска», «видеосвязь».
5. Если комнаты нет, обработка останавливается здесь. `find_room_by_id` возвращает `None`, срабатывает `http_not_found`, клиент получает 404 и шаблон `homepage/object_not_found.html` с текстом «Помещение не найдено.». Шаги ниже для этой комнаты не выполняются. До представления запрос при этом дошёл.
6. На сегодня (`date.today().isoformat()`, сейчас это `2026-10-28`) `is_room_available()` смотрит активные бронирования этой комнаты. В JSON даты `2026-09-29` и `2026-02-23`, на сегодня записи нет, функция возвращает `True`. `get_booking_status(True)` даёт текст «Переговорная свободна».
7. Представление вызывает `render(request, "rooms/room_detail.html", context)`. Загрузчик находит `rooms/templates/rooms/room_detail.html`. Шаблон расширяет `templates/base.html`, подключает навигацию, подставляет `{{ room.name }}`, `{{ room.capacity }}`, оборудование и значок статуса.
8. `HttpResponse` уходит со статусом 200. Браузер показывает карточку «Альфы», стили и скрипт года подвала.

Идентификатор передаётся в разных видах. В URL это текст `1`. После конвертера в представление приходит `int`. В шаблон данные комнаты приходят уже объектом `Room` из JSON, не из `request.GET`. В ссылках `{% url 'rooms:detail' room.id %}` число снова становится куском пути.

Нечисловой хвост вроде `/rooms/abc/` останавливается на шаге 2. В `room_detail` управления нет, срабатывает техническая 404 резолвера.
