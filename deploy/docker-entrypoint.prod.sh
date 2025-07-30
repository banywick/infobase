#!/bin/sh
set -e

# Ждем доступности БД (максимум 30 секунд)
timeout=30
while ! python manage.py check --database default >/dev/null 2>&1; do
timeout=$((timeout - 1))
    if [ $timeout -eq 0 ]; then
        echo "Postgres is unavailable - timed out"
        exit 1
    fi
echo "Postgres is unavailable - sleeping"
    sleep 1
done

# Применяем миграции
python manage.py migrate --noinput

# Запускаем основной процесс
exec "$@"