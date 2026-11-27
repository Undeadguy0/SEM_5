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
  number: 11,
  teacher: "Ящун Т.В.",
  teacher-position: "доц.",
  student: "Бунто М. В.",
  topic: "ФОРМЫ В DJANGO",
  year: 2026,
)

*Тема проекта:* система бронирования переговорных комнат (Roomly)

*Коммит гит:* 7f1e6ec

= Цель работы

Изучить создание, отображение, обработку и валидацию веб-форм в Django, освоить классы `Form` и `ModelForm`, создание и редактирование объектов по пользовательскому вводу и загрузку изображений; встроить формы в проект Roomly, сохранив его архитектуру, ORM-модели, шаблоны и правила предметной области.

= Созданные формы

#table(
  columns: (auto, auto, 1fr),
  [*Форма*], [*Тип*], [*Назначение*],
  [`BookingFilterForm`],
  [`forms.Form`],
  [фильтр списка `/bookings/`: дата, помещение, пользователь, статус, сортировка, тема; данные по GET, в базу ничего не пишет],

  [`BookingForm`],
  [`ModelForm`],
  [создание `/bookings/create/` и правка `/bookings/<id>/edit/` бронирования; поле `status` в форму не входит],

  [`RoomForm`],
  [`ModelForm`],
  [создание `/rooms/create/` и правка `/rooms/<slug>/edit/` помещения с загрузкой изображения],
)

= Фильтрация бронирований через GET-параметры

Форма фильтра связывается с `request.GET` только если параметры переданы; пустые статус и сортировка подставляются по умолчанию. После `is_valid()` значения берутся из `cleaned_data` (дата уже `date`, помещение — объект `Room`), неверные параметры дают сообщение над списком, а выборка остаётся на активных бронях. Поля выбора ограничены `ChoiceField`/`ModelChoiceField`, поэтому в `order_by()` попадают только ключи `SORT_FIELDS`.

```python
class BookingFilterForm(forms.Form):
    """Параметры фильтрации списка. Запись в базу не создаёт."""

    date = forms.DateField(
        required=False,
        label="Дата бронирования",
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={"type": "date", "class": "form-control"},
        ),
        error_messages={"invalid": "Укажите корректную дату."},
    )
    room = forms.ModelChoiceField(
        queryset=Room.objects.order_by("name"),
        required=False,
        label="Помещение",
        empty_label="Все помещения",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
```

```python
def bookings(request: HttpRequest) -> HttpResponse:
    """Показать бронирования с фильтрами и страницами."""
    if request.GET:
        submitted = request.GET.copy()
        if not submitted.get("status"):
            submitted["status"] = "active"
        if not submitted.get("sort"):
            submitted["sort"] = "date"
        form = BookingFilterForm(submitted)
    else:
        form = BookingFilterForm()

    error = ""
    booking_date = None
    room_id = None
    user_id = None
    query = ""
    sort = "date"
    status = "active"
    form_valid = form.is_bound and form.is_valid()
    if form_valid:
        booking_date = form.cleaned_data.get("date")
        room = form.cleaned_data.get("room")
        selected_user = form.cleaned_data.get("user")
        room_id = room.pk if room else None
        user_id = selected_user.pk if selected_user else None
        query = (form.cleaned_data.get("q") or "").strip()
        sort = form.cleaned_data.get("sort") or "date"
        status = form.cleaned_data.get("status") or "active"
    elif form.is_bound:
        error = "Проверьте корректность параметров фильтрации."
```


= Валидация данных и отображение ошибок

`BookingForm`: валидатор формата времени `validate_clock_time` (ЧЧ:ММ) подключается к полям времени в `__init__()`, `clean_booking_date()` запрещает прошедшую дату, `clean_start_time()`/`clean_end_time()` нормализуют время, `clean()` проверяет, что конец позже начала (`add_error("end_time", ...)`). Подписи, подсказки (`help_texts`) и виджеты Bootstrap (`type="date"`, `type="time"`, `form-select`) заданы в `Meta`.

```python
class BookingForm(forms.ModelForm):
    """Создание и редактирование бронирования.

    Поле status в форму не входит: новая запись получает статус
    модели по умолчанию, а при правке статус остаётся у объекта.
    """

    class Meta:
        """Поля, подписи и виджеты формы."""

        model = Booking
        fields = [
            "room",
            "booking_date",
            "start_time",
            "end_time",
            "user",
            "topic",
        ]
        labels = {
...
    def __init__(self, *args, **kwargs):
        """Подключить проверку формата времени."""
        super().__init__(*args, **kwargs)
        self.fields["start_time"].validators.append(validate_clock_time)
        self.fields["end_time"].validators.append(validate_clock_time)

    def clean_booking_date(self):
        """Запретить новую бронь на прошедшую дату.

        Returns:
            Дата, если она не раньше сегодняшнего дня.

        Raises:
            ValidationError: Если дата уже прошла.
        """
        booking_date = self.cleaned_data["booking_date"]
        if booking_date < timezone.localdate():
            raise ValidationError(
                "Нельзя создать бронирование на прошедшую дату.",
            )
        return booking_date
...
    def clean(self):
        """Проверить, что интервал времени не перевёрнут.

        Returns:
            Словарь проверенных значений.
        """
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        if start_time and end_time and start_time >= end_time:
            self.add_error(
                "end_time",
                "Время окончания должно быть позже времени начала.",
            )
        return cleaned_data
```

Шаблон `booking_form.html` выводит для каждого поля подпись, подсказку и ошибки, а общие ошибки формы (занятость помещения) — через `non_field_errors`:

```html
<form method="post">
    {% csrf_token %}
    {% for field in form %}
        <div class="mb-3">
            {{ field.label_tag }}
            {{ field }}
            {% if field.help_text %}
                <div class="form-text">{{ field.help_text }}</div>
            {% endif %}
            {% for error in field.errors %}
                <div class="text-danger">{{ error }}</div>
            {% endfor %}
        </div>
    {% endfor %}
    {% for error in form.non_field_errors %}
        <div class="alert alert-danger">{{ error }}</div>
    {% endfor %}
```


= Создание и редактирование бронирований, проверка доступности

GET отдаёт пустую форму (дата по умолчанию — сегодня) или форму с `instance`, POST — связанную форму. После `is_valid()` проверяется занятость: есть ли активная бронь на это помещение и дату; при правке текущая запись исключается `exclude(pk=booking.pk)`. Отменённые и завершённые брони в `active()` не входят и помещение не блокируют. При конфликте — `form.add_error(None, ...)`, иначе `form.save()` и `redirect` на список. Править можно только активную бронь, отсутствующий `id` даёт страницу 404 «Бронирование не найдено.».

```python
def booking_create(request: HttpRequest) -> HttpResponse:
    """Создать бронирование из ModelForm."""
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            room = form.cleaned_data["room"]
            booking_date = form.cleaned_data["booking_date"]
            is_booked = (
                Booking.objects.active()
                .filter(room=room, booking_date=booking_date)
                .exists()
            )
            if is_booked:
                form.add_error(None, OCCUPIED_MESSAGE)
            else:
                form.save()
                return redirect("bookings:bookings")
    else:
        form = BookingForm(
            initial={"booking_date": timezone.localdate()},
        )
    return render(
        request,
        "bookings/booking_form.html",
        {"form": form},
    )


def booking_update(
    request: HttpRequest,
    booking_id: int,
) -> HttpResponse:
    """Изменить активное бронирование."""
    try:
        booking = get_object_or_404(
            Booking.objects.active(),
            pk=booking_id,
        )
    except Http404:
        return _missing_booking(request)
    if request.method == "POST":
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            room = form.cleaned_data["room"]
            booking_date = form.cleaned_data["booking_date"]
            is_booked = (
                Booking.objects.active()
                .filter(room=room, booking_date=booking_date)
                .exclude(pk=booking.pk)
                .exists()
            )
            if is_booked:
                form.add_error(None, OCCUPIED_MESSAGE)
            else:
                form.save()
                return redirect("bookings:bookings")
    else:
        form = BookingForm(instance=booking)
    context = {"form": form, "booking": booking}
    return render(request, "bookings/booking_form.html", context)
```



= Отмена бронирования

Отмена — отдельный маршрут `<int:booking_id>/cancel/`, только POST (`@require_POST`, GET даёт 405), кнопка в списке и на карточке — форма `method="post"` с `{% csrf_token %}`. Запись не удаляется: `Booking.cancel()` ставит статус `cancelled`.

```python
@require_POST
def booking_cancel(
    request: HttpRequest,
    booking_id: int,
) -> HttpResponse:
    """Отменить активное бронирование, не удаляя запись."""
    try:
        booking = get_object_or_404(
            Booking.objects.active(),
            pk=booking_id,
        )
    except Http404:
        return _missing_booking(request)
    booking.cancel()
    return redirect("bookings:bookings")
```


= Загрузка изображений помещений

В модель `Room` добавлено `image = models.ImageField(upload_to="rooms/", blank=True, null=True)` (миграция `0008_room_image`, зависимость `Pillow`), в `settings.py` — `MEDIA_URL = "/media/"` и `MEDIA_ROOT = BASE_DIR / "media"`, в `roomly/urls.py` при `DEBUG` — `static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)`; каталог `media/` исключён из git. `RoomForm` ограничивает размер файла 2 МБ и вместимость не меньше 1, шаблон формы отправляется с `enctype="multipart/form-data"`, представление передаёт в форму `request.FILES`:

```python
def room_create(request: HttpRequest) -> HttpResponse:
    """Создать помещение и сохранить загруженное изображение."""
    if request.method == "POST":
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            room = form.save()
            return redirect(room.get_absolute_url())
    else:
        form = RoomForm()
    return render(
        request,
        "rooms/room_form.html",
        {"form": form},
    )
```


= Проверка пользовательских сценариев

Сценарии покрыты тестами `tests/test_pr11.py`: фильтр сохраняет значения и отклоняет неверную дату; создание, правка, проверка занятости и отмена бронирования; загрузка изображения помещения; POST без CSRF-токена получает 403. README.md дополнен описанием этапа ПР11.

#[
  ```bash
    $ python manage.py check
  System check identified no issues (0 silenced).
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
  collecting ... collected 46 items

  tests/test_bookings.py::test_is_room_available_empty PASSED              [  2%]
  tests/test_bookings.py::test_one_active_booking_per_room_and_date PASSED [  4%]
  tests/test_bookings.py::test_create_booking_rejects_bad_interval PASSED  [  6%]
  tests/test_bookings.py::test_create_booking_fields PASSED                [  8%]
  tests/test_bookings.py::test_cancel_booking_keeps_object PASSED          [ 10%]
  tests/test_bookings.py::test_find_booking_by_id PASSED                   [ 13%]
  tests/test_bookings.py::test_get_booking_status PASSED                   [ 15%]
  tests/test_bookings.py::test_find_bookings_by_organizer PASSED           [ 17%]
  tests/test_bookings.py::test_get_room_schedule PASSED                    [ 19%]
  tests/test_models.py::test_room_attributes_and_methods PASSED            [ 21%]
  tests/test_models.py::test_room_from_data_and_to_dict PASSED             [ 23%]
  tests/test_models.py::test_room_without_equipment PASSED                 [ 26%]
  tests/test_models.py::test_user_from_data_and_str PASSED                 [ 28%]
  tests/test_models.py::test_booking_links_objects_and_cancel PASSED       [ 30%]
  tests/test_pr10.py::test_status_slug_and_generated_field PASSED          [ 32%]
  tests/test_pr11.py::test_filter_form_keeps_values_and_rejects_bad_date PASSED [ 34%]
  tests/test_pr11.py::test_create_edit_and_cancel_booking PASSED           [ 36%]
  tests/test_pr11.py::test_room_image_upload PASSED                        [ 39%]
  tests/test_pr11.py::test_create_form_requires_csrf_token PASSED          [ 41%]
  tests/test_rooms.py::test_add_room PASSED                                [ 43%]
  tests/test_rooms.py::test_add_room_assigns_next_id PASSED                [ 45%]
  tests/test_rooms.py::test_find_room_by_id PASSED                         [ 47%]
  tests/test_rooms.py::test_find_room PASSED                               [ 50%]
  tests/test_rooms.py::test_check_room_capacity PASSED                     [ 52%]
  tests/test_rooms.py::test_filter_rooms_by_equipment PASSED               [ 54%]
  tests/test_rooms.py::test_filter_rooms_by_capacity PASSED                [ 56%]
  tests/test_rooms.py::test_sort_rooms PASSED                              [ 58%]
  tests/test_storage.py::test_rooms_roundtrip_keeps_id PASSED              [ 60%]
  tests/test_storage.py::test_users_roundtrip PASSED                       [ 63%]
  tests/test_storage.py::test_load_missing_files PASSED                    [ 65%]
  tests/test_storage.py::test_load_broken_json PASSED                      [ 67%]
  tests/test_storage.py::test_load_wrong_shape PASSED                      [ 69%]
  tests/test_storage.py::test_bookings_roundtrip_links_objects PASSED      [ 71%]
  tests/test_storage.py::test_load_bookings_skips_missing_links PASSED     [ 73%]
  tests/test_users.py::test_add_user PASSED                                [ 76%]
  tests/test_users.py::test_find_user_by_name PASSED                       [ 78%]
  tests/test_users.py::test_find_users_by_substring PASSED                 [ 80%]
  tests/test_web.py::test_index_has_navigation PASSED                      [ 82%]
  tests/test_web.py::test_room_list_and_detail PASSED                      [ 84%]
  tests/test_web.py::test_booking_list_and_detail PASSED                   [ 86%]
  tests/test_web.py::test_available_rooms_by_date PASSED                   [ 89%]
  tests/test_web.py::test_statistics_page PASSED                           [ 91%]
  tests/test_web.py::test_unknown_url_uses_custom_404 PASSED               [ 93%]
  tests/test_web.py::test_room_search_by_name_and_equipment PASSED         [ 95%]
  tests/test_web.py::test_available_rooms_reject_bad_date PASSED           [ 97%]
  tests/test_web.py::test_booking_filters_sort_and_search PASSED           [100%]

  ============================== 46 passed in 1.16s ==============================
  ```

  ```bash
  $ flake8 . --extend-exclude=venv
  ```
]

= Git

Коммит `7f1e6ec` — «PR11: формы Django для бронирований и изображений».

= Вывод

В результате выполнения ПР11 в Roomly ввод и проверка пользовательских данных выполняются формами Django: фильтр списка работает через GET-форму, бронирования создаются и редактируются через `ModelForm` с проверкой даты, времени и занятости помещения, отмена меняет статус POST-запросом с CSRF-защитой, у помещений появилась загрузка изображений. Проверки и тесты проходят.

= Ответы на контрольные вопросы

+ *Для чего предназначены формы Django?* \
  Формы Django описывают поля, забирают ввод из запроса, превращают его в типы Python, проверяют и отдают шаблону подписи, значения и ошибки. Сами по себе они не маршруты и не замена моделей.
+ *Чем отличаются классы Form и ModelForm?* \
  `Form` — поля пишет разработчик, к одной модели она не привязана. Так сделан фильтр. `ModelForm` берёт поля из модели и умеет создать или обновить запись через `save()`. Так сделаны бронь и помещение.
+ *В чём разница между GET- и POST-запросами при отправке формы?* \
  GET кладёт параметры в адрес и подходит для фильтра. Его можно открыть снова, токен CSRF обычной форме не нужен. POST кладёт данные в тело и используется, когда запись создаётся, меняется или отменяется. Такой запрос в Django защищается CSRF.
+ *Что означает свойство is\_bound и в каких случаях оно используется?* \
  `is_bound` истинно, если форме передали данные. У `/bookings/` без параметров форма несвязанная. У `/bookings/?date=2026-09-29` связанная. Несвязанную форму не проверяют как ошибочную: пользователь ещё ничего не отправил.
+ *Для чего вызывается метод is\_valid()?* \
  `is_valid()` запускает проверку полей, валидаторы, `clean_<поле>()` и `clean()`. Пока он не вернул `True`, данные не используют и `save()` не вызывают.
+ *Что содержит атрибут cleaned\_data и когда к нему можно обращаться?* \
  `cleaned_data` — словарь уже проверенных значений: дата стала `date`, комната — объектом `Room`, а не строкой id. Читать его можно после успешного `is_valid()`. Иначе словаря может не быть или в нём не хватает полей.
+ *Для чего предназначен метод clean\_\<field\>()? Чем он отличается от метода clean()?* \
  `clean_booking_date()` проверяет одно поле и возвращает его значение. `clean()` видит несколько полей сразу. Поэтому интервал «начало раньше конца» живёт в `clean()`, а запрет прошлой даты — в `clean_booking_date()`.
+ *Как в Django реализуется проверка введённых пользователем данных? Для чего используется ValidationError?* \
  Сначала тип и обязательность поля, потом валидаторы, потом методы `clean_...` и `clean()`. `ValidationError` сообщает Django текст ошибки. Для одного поля его бросают из `clean_<поле>` или валидатора. Для пары полей чаще вызывают `add_error`.
+ *Для чего применяются виджеты (widgets) и как они влияют на отображение полей формы?* \
  Виджет решает, какой HTML получится из поля: `DateInput`, `Select`, `ClearableFileInput`. На значение в базе он не влияет. `attrs` добавляет `type`, `class` и другие атрибуты. Поэтому дата в браузере — календарь, а не просто текст.
+ *Как связать ModelForm с моделью Django и ограничить набор полей, доступных для редактирования?* \
  В `Meta` стоят `model = Booking` и явный список `fields`. `"__all__"` не используется, чтобы новое служебное поле модели само не попало в форму. `status`, `slug` и `is_large` пользователю не отдаются.
+ *В чём разница между созданием и редактированием объекта с помощью ModelForm? Для чего при редактировании используется параметр instance?* \
  Без `instance` `save()` делает `INSERT`. С `instance=booking` форма заполняется текущими значениями, а `save()` обновляет эту строку. id не меняется.
+ *Как организовать обработку формы в view-функции при GET- и POST-запросах?* \
  GET: пустая или заполненная из объекта форма и `render`. POST: форма из `request.POST` (и `request.FILES`, если есть файл), `is_valid()`, при успехе действие и `redirect`. При ошибке снова `render` той же формы, значения и тексты ошибок сохраняются.
+ *Для чего используется метод save() формы ModelForm?* \
  `save()` записывает проверенные данные формы в модель. Его вызывают только после `is_valid()`. `commit=False` собирает объект в памяти и даёт представлению дописать поля до второго `save()`. Здесь этого нет: все нужные связи выбираются в форме.
+ *Как реализовать проверку доступности помещения на выбранную дату с учётом существующих активных бронирований?* \
  После проверки формы берём комнату и дату из `cleaned_data` и спрашиваем `Booking.objects.active().filter(room=..., booking_date=...).exists()`. При правке добавляем `exclude(pk=booking.pk)`. Отменённые и завершённые в `active()` не попадают и комнату не держат.
+ *Почему при отмене бронирования следует изменять его статус, а не удалять запись из базы данных?* \
  Отмена — смена состояния, а не исчезновение факта. История нужна списку «Отменённые», админке и правилу «отменённая бронь комнату освобождает». `delete()` стёр бы строку, и это было бы не отличить от «брони никогда не было».
+ *Для чего используется request.FILES и какую роль играет атрибут enctype="multipart/form-data" при отправке файлов?* \
  Файл приходит не в `request.POST`, а в `request.FILES`. Браузер кладёт его в запрос только если у формы стоит `enctype="multipart/form-data"`. Без атрибута до представления дойдёт пустой файл. В форму передают оба словаря: `RoomForm(request.POST, request.FILES)`.
+ *Как защитить POST-запросы от межсайтовой подделки запросов (CSRF) в Django?* \
  В шаблоне `{% csrf_token %}` выводит скрытое поле. Middleware сверяет его с cookie. Чужой сайт не знает token и не может отправить POST от имени пользователя. На проекте middleware `CsrfViewMiddleware` включён. Проверка: клиент с `enforce_csrf_checks` и POST без токена получает 403, запись не создаётся. Это делает `tests/test_pr11.py`.
+ *Как организовать переход к редактированию конкретного бронирования и обработать ситуацию, когда объект не найден?* \
  Ссылка «Редактировать» строится как `{% url 'bookings:booking_update' booking.id %}`, маршрут `<int:booking_id>/edit/`. В представлении `get_object_or_404` по активным броням. Нет id или бронь уже не активна — ответ 404 «Бронирование не найдено.», не 500.
