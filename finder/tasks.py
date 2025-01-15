# import os
# import pandas as pd
# import pytz
# from sqlalchemy import create_engine
# from celery import shared_task
# from datetime import datetime
# from finder.models import Data_Table
# from inventory.models import OrderInventory


# @shared_task
# def data_save_db(file_url):
#     try:
#         # Шаблон колонок
#         columns_template = [
#             "Цена",
#             "Комментарий",
#             "Код",
#             "Артикул",
#             "Партия.Код",
#             "Номенклатура",
#             "Базовая единица измерения",
#             "Склад",
#             "Конечный остаток (Количество)",
#         ]

#         # Читаем файл
#         df = pd.read_excel(file_url, usecols=[0, 11, 12, 13, 14, 15, 16, 17, 18])
        
#         # Проверяем порядок столбцов
#         order_columns = df.iloc[7].fillna("Конечный остаток (Количество)").tolist()
#         if order_columns != columns_template:
#             raise ValueError("Не соответствует порядок столбцов в документе")

#         # Удаляем первые 10 строк
#         df = df.iloc[10:]

#         # Переименование колонок
#         df.columns = [
#             "price",
#             "comment",
#             "code",
#             "article",
#             "party",
#             "title",
#             "base_unit",
#             "project",
#             "quantity",
#         ]

#         # Обработка данных
#         df["quantity"] = df["quantity"].astype(float).round(2)

#         # Сохранение в базу данных
#         engine = create_engine("postgresql://sklad:sklad@127.0.0.1:5432/sklad_db")
#         df.to_sql("finder_remains", engine, if_exists="replace", index_label="id")
#         success_message = 'Данные успешно загружены'  # Задаем сообщение об успехе


#     except Exception as e:
#         raise ValueError(f"Ошибка при обработке файла: {e}")

#     finally:
#         # Удаляем файл вне зависимости от результата выполнения
#         if file_url and os.path.exists(file_url):
#             os.remove(file_url)

#     return success_message  # Возвращаем сообщение об успехе (или None, если была ошибка)
    


# def backup_sahr_table():
#     timezone = pytz.timezone('Europe/Minsk')
#     current_date = datetime.now(timezone).strftime('%d.%m.%Y %H:%M:%S')
#     queryset = Data_Table.objects.all()  # Получите все записи из модели
#     df = pd.DataFrame(list(queryset.values()))  # Преобразуйте в DataFrame
#     df.drop(df.columns[[0, 1]], axis=1, inplace=True)
#     folder_path = 'finder/document/backup_sahr'  # Замените на свой путь
#     # Сохраняем в файл Excel с читаемой датой в названии
#     file_path = os.path.join(folder_path, f'CAXP_{current_date}.xlsx')
#     n = f'CAXP_{current_date}.xlsx'
#     df.to_excel(file_path, index=False)
#     filename = f'CAXP_{current_date}.xlsx'
#     return [file_path, filename]  


# def backup_inventory_table():
#     timezone = pytz.timezone('Europe/Minsk')
#     current_date = datetime.now(timezone).strftime('%d.%m.%Y %H:%M:%S')
    
#     # Получите данные из базы
#     queryset = OrderInventory.objects.select_related('product', 'user').values(
#         'user__username',
#         'product__article', 
#         'product__title', 
#         'product__base_unit', 
#         'product__status', 
#         'quantity_ord', 
#         'created_at', 
#         'address', 
#         'comment',
#     ).filter(product__status__iexact='Сошлось')
    
#     # Преобразование в DataFrame
#     df = pd.DataFrame(list(queryset))

#     # Переименовываем столбцы
#     df.rename(columns={
#         'user__username': 'Пользователь',
#         'product__article': 'Артикул',
#         'product__title': 'Наименование',
#         'product__base_unit': 'Единица',
#         'quantity_ord': 'Посчитанно',
#         'address': 'Адрес',
#         'comment': 'Комментарий',
#         'created_at': 'Дата создания',
#         'product__status': 'Статус',
#     }, inplace=True)

#     # Задайте порядок столбцов
#     columns_order = ['Пользователь','Артикул', 'Наименование', 
#                     'Единица', 'Посчитанно', 'Адрес', 'Комментарий',
#                     'Дата создания', 'Статус']  # Замените на нужный порядок
#     df = df[columns_order]  # Измените порядок столбцов
    
#     # Задайте путь к папке и создайте его, если он не существует
#     folder_path = os.path.join('finder', 'document', 'report_inventory')  # путь к папке
#     os.makedirs(folder_path, exist_ok=True)
    
#     # Сохраняем в файл Excel с читаемой датой в названии
#     file_path = os.path.join(folder_path, f'report_inv.xlsx')
#     df.to_excel(file_path, index=True)
    
#     return [file_path, f'report_inv.xlsx']



