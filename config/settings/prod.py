from .base import *

DEBUG = False
ALLOWED_HOSTS = ['172.17.10.208', 'localhost', '127.0.0.1']

#Security
# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True
# SECURE_SSL_REDIRECT = True

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