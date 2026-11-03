#import "@local/mirea_title_list:1.0.0": *
#import "@local/gost:1.0.0": *
#import "@preview/codly:2.0.0" as codly

#show: make-gost


#titlepage(
  discipline: "Разработка приложений на базе фреймворков",
  group: "ЭФБО-16-24",
  number: 5,
  teacher: "Ящун Т.В.",
  teacher-position: "доц.",
  student: "Бунто М. В.",
  topic: "DJANGO, HTTP И ОСНОВЫ ВЕБ-РАЗРАБОТКИ",
  year: 2026,
)

*Тема проекта:* система бронирования переговорных комнат

*Коммит гит:* d200cb5

*Результаты проверки:*
#[
  #show: codly.theme("dark")
  #show raw.where(block: true): codly.new
  ```bash
  F15/undeadguy /home/undeadguy/ПАРЫ/Разработка на базе Фреймворков❯ python manage.py check
  System check identified no issues (0 silenced).
  ```

  ```bash
    F15/undeadguy /home/undeadguy/ПАРЫ/Разработка на базе Фреймворков❯ pytest -v
  ========================================================================================================================= test session starts ==========================================================================================================================
  platform linux -- Python 3.12.13, pytest-9.1.1, pluggy-1.6.0 -- /mnt/ПРОЕКТЫ/ПАРЫ/Разработка на базе Фреймворков/venv/bin/python3.12
  cachedir: .pytest_cache
  rootdir: /mnt/ПРОЕКТЫ/ПАРЫ/Разработка на базе Фреймворков
  configfile: pyproject.toml
  testpaths: tests
  collected 36 items                                                                                                                                                                                                                                                     

  tests/test_bookings.py::test_is_room_available_empty PASSED                                                                                                                                                                                                      [  2%]
  tests/test_bookings.py::test_one_active_booking_per_room_and_date PASSED                                                                                                                                                                                         [  5%]
  tests/test_bookings.py::test_create_booking_rejects_bad_interval PASSED                                                                                                                                                                                          [  8%]
  tests/test_bookings.py::test_create_booking_fields PASSED                                                                                                                                                                                                        [ 11%]
  tests/test_bookings.py::test_cancel_booking_keeps_object PASSED                                                                                                                                                                                                  [ 13%]
  tests/test_bookings.py::test_find_booking_by_id PASSED                                                                                                                                                                                                           [ 16%]
  tests/test_bookings.py::test_get_booking_status PASSED                                                                                                                                                                                                           [ 19%]
  tests/test_bookings.py::test_find_bookings_by_organizer PASSED                                                                                                                                                                                                   [ 22%]
  tests/test_bookings.py::test_get_room_schedule PASSED                                                                                                                                                                                                            [ 25%]
  tests/test_models.py::test_room_attributes_and_methods PASSED                                                                                                                                                                                                    [ 27%]
  tests/test_models.py::test_room_from_data_and_to_dict PASSED                                                                                                                                                                                                     [ 30%]
  tests/test_models.py::test_room_without_equipment PASSED                                                                                                                                                                                                         [ 33%]
  tests/test_models.py::test_user_from_data_and_str PASSED                                                                                                                                                                                                         [ 36%]
  tests/test_models.py::test_booking_links_objects_and_cancel PASSED                                                                                                                                                                                               [ 38%]
  tests/test_rooms.py::test_add_room PASSED                                                                                                                                                                                                                        [ 41%]
  tests/test_rooms.py::test_add_room_assigns_next_id PASSED                                                                                                                                                                                                        [ 44%]
  tests/test_rooms.py::test_find_room_by_id PASSED                                                                                                                                                                                                                 [ 47%]
  tests/test_rooms.py::test_find_room PASSED                                                                                                                                                                                                                       [ 50%]
  tests/test_rooms.py::test_check_room_capacity PASSED                                                                                                                                                                                                             [ 52%]
  tests/test_rooms.py::test_filter_rooms_by_equipment PASSED                                                                                                                                                                                                       [ 55%]
  tests/test_rooms.py::test_filter_rooms_by_capacity PASSED                                                                                                                                                                                                        [ 58%]
  tests/test_rooms.py::test_sort_rooms PASSED                                                                                                                                                                                                                      [ 61%]
  tests/test_storage.py::test_rooms_roundtrip_keeps_id PASSED                                                                                                                                                                                                      [ 63%]
  tests/test_storage.py::test_users_roundtrip PASSED                                                                                                                                                                                                               [ 66%]
  tests/test_storage.py::test_load_missing_files PASSED                                                                                                                                                                                                            [ 69%]
  tests/test_storage.py::test_load_broken_json PASSED                                                                                                                                                                                                              [ 72%]
  tests/test_storage.py::test_load_wrong_shape PASSED                                                                                                                                                                                                              [ 75%]
  tests/test_storage.py::test_bookings_roundtrip_links_objects PASSED                                                                                                                                                                                              [ 77%]
  tests/test_storage.py::test_load_bookings_skips_missing_links PASSED                                                                                                                                                                                             [ 80%]
  tests/test_users.py::test_add_user PASSED                                                                                                                                                                                                                        [ 83%]
  tests/test_users.py::test_find_user_by_name PASSED                                                                                                                                                                                                               [ 86%]
  tests/test_users.py::test_find_users_by_substring PASSED                                                                                                                                                                                                         [ 88%]
  tests/test_web.py::test_index_has_navigation PASSED                                                                                                                                                                                                              [ 91%]
  tests/test_web.py::test_room_list_and_detail PASSED                                                                                                                                                                                                              [ 94%]
  tests/test_web.py::test_booking_list_and_detail PASSED                                                                                                                                                                                                           [ 97%]
  tests/test_web.py::test_unknown_url_uses_custom_404 PASSED                                                                                                                                                                                                       [100%]

  ========================================================================================================================== 36 passed in 0.08s =================================================================
  ```

  ```bash
    F15/undeadguy /home/undeadguy/ПАРЫ/Разработка на базе Фреймворков❯ flake8 . --extend-exclude=venv
    F15/undeadguy /home/undeadguy/ПАРЫ/Разработка на базе Фреймворков❯ 
  ```
]

*Вывод:* В результате выполнения ПР6 веб-часть индивидуального проекта
переведена с формирования HTML в Python на систему шаблонов Django.
