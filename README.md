# Информационная база узкой специализации

Этот проект представляет собой информационную базу узкой специализации, реализованную с использованием Django и Django Rest Framework (DRF). Проект использует PostgreSQL в качестве базы данных и Redis вместе с Celery для выполнения фоновых задач.

## Требования

Для запуска проекта необходимо установить следующие компоненты:

- Python 3.x
- PostgreSQL
- Redis
- Celery

## Установка

1. **Клонируйте репозиторий:**

    ```bash
    git clone <URL вашего репозитория>
    cd <имя вашего проекта>
    ```

2. **Создайте виртуальное окружение и активируйте его:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # На Windows используйте `venv\Scripts\activate`
    ```

3. **Установите зависимости:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Настройте базу данных PostgreSQL:**

    Убедитесь, что PostgreSQL установлен и запущен. Создайте базу данных и пользователя, используя следующие команды:

    ```sql
    CREATE DATABASE <имя вашей базы данных>;
    CREATE USER <имя пользователя> WITH PASSWORD '<пароль>';
    GRANT ALL PRIVILEGES ON DATABASE <имя вашей базы данных> TO <имя пользователя>;
    ```

    Обновите файл `settings.py` с настройками вашей базы данных:

    ```python
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': '<имя вашей базы данных>',
            'USER': '<имя пользователя>',
            'PASSWORD': '<пароль>',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }
    ```

5. **Запустите миграции:**

    ```bash
    python manage.py migrate
    ```

6. **Запустите сервер разработки:**

    ```bash
    python manage.py runserver
    ```

## Запуск Celery

Для выполнения фоновых задач используется Celery. Чтобы запустить Celery, выполните следующую команду:

```bash
celery -A config worker --loglevel=info
