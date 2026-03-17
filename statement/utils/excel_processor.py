# excel_processor.py
import os
import openpyxl
from datetime import datetime

class ExcelProcessor:
    """
    Обработчик Excel файлов
    """
    
    def __init__(self):
        self.last_row_count = 0
    
    def process_column_b(self, input_file, column_index=2, output_folder=None):
        """
        Читает указанный столбец из исходного файла и создает новый файл с этими данными
        
        Args:
            input_file: путь к исходному файлу
            column_index: индекс столбца (1=A, 2=B, 3=C, ...)
            output_folder: папка для сохранения результата (если None, используется папка исходного файла)
        
        Returns:
            str: путь к созданному файлу с результатами
        """
        print(f"📊 Открываем файл: {input_file}")
        
        # Проверяем существование файла
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Файл не найден: {input_file}")
        
        # Открываем исходный файл
        try:
            wb = openpyxl.load_workbook(input_file, data_only=True)
            sheet = wb.active
            print(f"📋 Активный лист: {sheet.title}")
        except Exception as e:
            raise Exception(f"Ошибка при открытии Excel файла: {e}")
        
        # Собираем данные из указанного столбца
        column_data = []
        empty_cells = 0
        
        for row in sheet.iter_rows(min_col=column_index, max_col=column_index):
            for cell in row:
                if cell.value is not None and str(cell.value).strip():
                    column_data.append(str(cell.value).strip())
                else:
                    empty_cells += 1
        
        self.last_row_count = len(column_data)
        
        print(f"📋 Найдено строк с данными: {len(column_data)}")
        print(f"📋 Пустых ячеек: {empty_cells}")
        
        if len(column_data) == 0:
            print("⚠️ В столбце нет данных!")
            # Создаем файл с заголовком
            column_data = ["Нет данных в столбце B"]
        
        # Создаем новый файл с результатами
        result_wb = openpyxl.Workbook()
        result_sheet = result_wb.active
        result_sheet.title = "Результат"
        
        # Записываем данные
        for i, value in enumerate(column_data, 1):
            result_sheet.cell(row=i, column=1, value=value)
        
        # Добавляем заголовок
        result_sheet.cell(row=1, column=2, value=f"Всего строк: {len(column_data)}")
        result_sheet.cell(row=2, column=2, value=f"Обработано: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Формируем имя для результата
        if output_folder is None:
            output_folder = os.path.dirname(input_file)
        
        base_name = os.path.basename(input_file)
        name_without_ext = os.path.splitext(base_name)[0]
        result_filename = f"{name_without_ext}_столбец_B_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        result_path = os.path.join(output_folder, result_filename)
        
        # Сохраняем
        result_wb.save(result_path)
        print(f"💾 Результат сохранен: {result_path}")
        
        return result_path
    
    def process_with_projects(self, input_file, projects, output_folder=None):
        """
        Обработка с учетом выбранных проектов
        Здесь можно реализовать фильтрацию данных по проектам
        
        Args:
            input_file: путь к исходному файлу
            projects: список выбранных проектов
            output_folder: папка для сохранения результата
        """
        print(f"📊 Обработка для проектов: {projects}")
        
        # Пока просто вызываем базовую обработку
        # В будущем здесь можно добавить фильтрацию по проектам
        result_file = self.process_column_b(
            input_file=input_file,
            column_index=2,
            output_folder=output_folder
        )
        
        # Добавляем информацию о проектах в результат
        try:
            wb = openpyxl.load_workbook(result_file)
            sheet = wb.active
            
            # Добавляем информацию о проектах на отдельный лист
            projects_sheet = wb.create_sheet("Проекты")
            projects_sheet.cell(row=1, column=1, value="ID проекта")
            projects_sheet.cell(row=1, column=2, value="Номер проекта")
            
            for i, proj in enumerate(projects, 2):
                projects_sheet.cell(row=i, column=1, value=proj.get('id'))
                projects_sheet.cell(row=i, column=2, value=proj.get('project'))
            
            wb.save(result_file)
            print(f"📝 Информация о проектах добавлена в файл")
            
        except Exception as e:
            print(f"⚠️ Не удалось добавить информацию о проектах: {e}")
        
        return result_file