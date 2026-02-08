#!/bin/sh

set -e

echo "Очищаем статические файлы..."
rm -rf /app/staticfiles/*

echo "Собираем статические файлы с манифестом..."
python manage.py collectstatic --noinput --clear

echo "Проверяем создание манифеста..."
if [ -f "/app/staticfiles/staticfiles.json" ]; then
    echo "✓ Манифест создан успешно"
    echo "Пример записей:"
    python -c "
import json
with open('/app/staticfiles/staticfiles.json') as f:
    data = json.load(f)
    for i, (k, v) in enumerate(list(data.items())[:3]):
        print(f'  {k} → {v}')
    print(f'Всего записей: {len(data)}')
"
else
    echo "✗ Манифест не создан!"
    exit 1
fi

echo "Запуск сервера..."
exec "$@"