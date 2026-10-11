"""Подключение Django к тестам, если пакет установлен."""

import importlib.util
import os


if importlib.util.find_spec("django") is not None:
    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "roomly.settings")
    django.setup()
