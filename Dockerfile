FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY . .

# Создаем пользователя для безопасности (опционально)
RUN adduser --disabled-password --gecos '' myuser

# Переключаемся на непривилегированного пользователя
USER myuser