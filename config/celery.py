import os
from celery import Celery

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")  # Явно указываем dev

app = Celery("config")  # Используем имя основного модуля вместо finder

# Загружаем настройки из Django, используя namespace CELERY
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоподгрузка задач из всех зарегистрированных приложений
app.autodiscover_tasks()