from django.http import HttpResponse
from mimetypes import guess_type
import os
import pandas as pd
import pytz
from datetime import datetime
from ..models import Data_Table

def handle_backup_download(file_path, filename):
    """Обработка скачивания резервной копии."""
    # Определение MIME-типа файла
    mime_type, _ = guess_type(file_path)

    # Отправка файла как HTTP-ответ
    with open(file_path, 'rb') as file:
        response = HttpResponse(file, content_type=mime_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    



def backup_sahr_table():
    timezone = pytz.timezone('Europe/Minsk')
    current_date = datetime.now(timezone).strftime('%d.%m.%Y')
    queryset = Data_Table.objects.all()  # Получите все записи из модели
    df = pd.DataFrame(list(queryset.values()))  # Преобразуйте в DataFrame
    df.drop(df.columns[[0, 1]], axis=1, inplace=True)

    # Преобразуем все столбцы, которые могут быть временными метками, в формат без часового пояса
    for col in df.columns:
        try:
            df[col] = pd.to_datetime(df[col], errors='ignore').dt.tz_localize(None)
        except AttributeError:
            pass  # Если столбец не содержит временные метки, просто пропускаем его

    folder_path = 'sahr/document/backup_sahr'  # Замените на свой путь

    # Создаем директорию, если она не существует
    os.makedirs(folder_path, exist_ok=True)

    # Сохраняем в файл Excel с читаемой датой в названии
    file_path = os.path.join(folder_path, f'CAXP_{current_date}.xlsx')
    filename = f'CAXP_{current_date}.xlsx'
    df.to_excel(file_path, index=False)
    return file_path, filename