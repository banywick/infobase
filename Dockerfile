FROM python:3.12-slim-bookworm  

# Оптимизация Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Установка зависимостей
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    postgresql-client && \
    apt-get purge -y --auto-remove && \
    rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /usr/src/app

# Копирование зависимостей
COPY requirements.txt .

# Установка Python-зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование проекта
COPY . .

# Команда по умолчанию (переопределяется в docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]