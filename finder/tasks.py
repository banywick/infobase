import os
import pandas as pd
from sqlalchemy import create_engine
from celery import shared_task


# Проверка celery на работоспособность
@shared_task
def ping():
    return "pong"



@shared_task()
def data_save_db(file_url):
    try:
        # Шаблон колонок
        required_columns = [
            "Цена",
            "Партия.Примечание",
            "Комментарий",
            "Код",
            "Артикул",
            "Партия.Код",
            "Номенклатура",
            "Базовая единица измерения",
            "Склад",
            "Конечный остаток (Количество)",
        ]

        # Читаем строки 7 и 9 для поиска заголовков
        header_df = pd.read_excel(file_url, header=None, nrows=10)
        print(header_df)
        
        # Ищем основной заголовок "Конечный остаток" в 7 строке (индекс 6)
        seventh_row = header_df.iloc[6].fillna("").astype(str)
        quantity_col = None
        for col_idx, value in seventh_row.items():
            if "Конечный остаток" in value:
                quantity_col = col_idx
                break
        
        if quantity_col is None:
            raise ValueError("Не найден столбец 'Конечный остаток (Количество)' в 7 строке")
        
        # Ищем остальные заголовки в 9 строке (индекс 8)
        ninth_row = header_df.iloc[8].fillna("").astype(str)
        
        column_indices = {}
        missing_columns = []
        
        for col in required_columns:
            if col == "Конечный остаток (Количество)":
                column_indices[col] = quantity_col
                continue
                
            found = False
            for col_idx, value in ninth_row.items():
                if value.strip() == col:
                    column_indices[col] = col_idx
                    found = True
                    break
            if not found:
                missing_columns.append(col)
        
        if missing_columns:
            raise ValueError(f"Не найдены следующие столбцы в 9-й строке: {', '.join(missing_columns)}")
        
        # Упорядочиваем индексы согласно порядку в required_columns
        ordered_indices = [column_indices[col] for col in required_columns]
        
        # Читаем файл, пропуская первые 10 строк и используя только нужные столбцы
        df = pd.read_excel(
            file_url,
            usecols=ordered_indices,
            skiprows=10,
            header=None,
            names=[
                "price",
                "notes_part",
                "comment",
                "code",
                "article",
                "party",
                "title",
                "base_unit",
                "project",
                "quantity",
            ]
        )

        # Обработка данных
        df["quantity"] = df["quantity"].astype(float).round(2)

        # Сохранение в базу данных
        engine = create_engine("postgresql://sklad:sklad@127.0.0.1:5432/sklad_db")
        df.to_sql("finder_remains", engine, if_exists="replace", index_label="id")
        success_message = 'Данные успешно загружены'

    except Exception as e:
        error_message = f"Ошибка загрузки: {e}"
        raise ValueError(error_message)

    finally:
        # Удаляем файл вне зависимости от результата выполнения
        if file_url and os.path.exists(file_url):
            os.remove(file_url)

    print(success_message)
    return success_message