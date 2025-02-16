import os
import pandas as pd
from sqlalchemy import create_engine
from celery import shared_task




@shared_task
def data_save_db(file_url):
    try:
        # Шаблон колонок
        columns_template = [
            "Цена",
            "Комментарий",
            "Код",
            "Артикул",
            "Партия.Код",
            "Номенклатура",
            "Базовая единица измерения",
            "Склад",
            "Конечный остаток (Количество)",
        ]

        # Читаем файл
        df = pd.read_excel(file_url, usecols=[0, 11, 12, 13, 14, 15, 16, 17, 18])

        # Проверяем порядок столбцов
        order_columns = df.iloc[7].fillna("Конечный остаток (Количество)").tolist()
        if order_columns != columns_template:
            raise ValueError("Не соответствует порядок столбцов в документе")

        # Удаляем первые 10 строк
        df = df.iloc[10:]

        # Переименование колонок
        df.columns = [
            "price",
            "comment",
            "code",
            "article",
            "party",
            "title",
            "base_unit",
            "project",
            "quantity",
        ]

        # Обработка данных
        df["quantity"] = df["quantity"].astype(float).round(2)

        # Сохранение в базу данных
        engine = create_engine("postgresql://sklad:sklad@127.0.0.1:5432/sklad_db")
        df.to_sql("finder_remains", engine, if_exists="replace", index_label="id")
        success_message = 'Данные успешно загружены'
        # logger.info(success_message)

    except Exception as e:
        error_message = f"Ошибка загрузки: {e}"
        raise ValueError(error_message)

    finally:
        # Удаляем файл вне зависимости от результата выполнения
        if file_url and os.path.exists(file_url):
            os.remove(file_url)

    return success_message