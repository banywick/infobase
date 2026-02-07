from .base import *

DEBUG = False
ALLOWED_HOSTS = ['infobase-01.okbtsp.corp', 'localhost', '127.0.0.1']

# Настройки для работы за прокси
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# Static files - КЛЮЧЕВЫЕ НАСТРОЙКИ
STATIC_ROOT = '/app/static_prod'  # Папка для collectstatic
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    '/app/static',  # исходные файлы
]

# ВАЖНО: Используем Django's ManifestStaticFilesStorage для версионирования
# Он добавит хэши к именам файлов при collectstatic
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': 'db',
        'PORT': '5432',
    }
}

# Celery
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'