from .base import *

DEBUG = False
ALLOWED_HOSTS = ['infobase-01.okbtsp.corp', 'localhost', '127.0.0.1']

CSRF_COOKIE_SECURE = True    # Передавать CSRF-куки только по HTTPS
SESSION_COOKIE_SECURE = True # Передавать сессионные куки только по HTTPS
SECURE_SSL_REDIRECT = True   # Автоматически редиректить HTTP-запросы на HTTPS

# Static files
STATIC_ROOT = '/app/staticfiles'
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    '/app/static',  # основная папка static в корне проекта
]

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