FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY . .

# Создаем статические директории
RUN mkdir -p staticfiles media

# Делаем entrypoint исполняемым
RUN chmod +x /app/deploy/web-entrypoint.sh

# НЕ меняем пользователя для упрощения
# RUN adduser --disabled-password --gecos '' myuser
# USER myuser