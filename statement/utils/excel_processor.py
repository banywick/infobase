# excel_processor.py
import os
import openpyxl
from datetime import datetime
from typing import List, Dict, Optional, Union

from finder.utils.services.details_service import RemainsDetailService
from statement.utils.comparison_search_service import SearchService

class ExcelProcessor:
    """
    Обработчик Excel файлов с проверкой доступности материалов на проектах
    """
    
    def __init__(self):
        self.last_row_count = 0
        self.processed_range = None
        self.materials_found = 0
        self.materials_not_found = 0
        self.materials_insufficient = 0
    
    def check_material_availability(self, name: str, required: Union[int, float], projects: List[str]) -> Optional[Dict]:
        """
        Проверяет доступность материала на проектах
        
        Args:
            name: Наименование материала для поиска
            required: Требуемое количество
            projects: Список проектов для проверки (в порядке приоритета)
        
        Returns:
            Dict с информацией о материале или None
        """
        # Поиск в базе по наименованию
        search_results = SearchService.search_by_nomenclature(name)
        
        if not search_results.exists():
            return {
                'found': False,
                'name': name,
                'required': required,
                'error': 'Материал не найден в базе'
            }
        
        # Берем первый результат поиска
        first_result = search_results.first()
        accounting_code = getattr(first_result, 'accounting_code', None)
        
        if not accounting_code:
            return {
                'found': False,
                'name': name,
                'required': required,
                'error': 'Отсутствует accounting_code'
            }
        
        # Ищем по приоритетным проектам
        for project_name in projects:
            # Используем новый метод для получения количества по артикулу и проекту
            result = RemainsDetailService.get_total_quantity_by_article_and_project(
                article=accounting_code,
                project_name=project_name
            )
            
            if result and result.get('total_quantity', 0) > 0:
                quantity = result['total_quantity']
                
                return {
                    'found': True,
                    'name': name,
                    'nomenclature_kd': first_result.nomenclature_kd,
                    'article': result['article'],
                    'title': result.get('title', name),  # Если нет title, используем исходное имя
                    'required': required,
                    'quantity': quantity,
                    'project': result['project'],
                    'status_color': result.get('status_color', 'gray'),
                    'base_unit': result.get('base_unit', 'шт'),
                    'total_available': result.get('total_quantity', 0),  # Общее количество по проекту
                    'sufficient': quantity >= required,
                    'party': [p['party'] for p in result.get('positions_details', [])] if result.get('positions_details') else []
                }
        
        # Если ни один проект не подошел, но материал существует где-то
        # Получаем общую информацию о материале
        detail_data = RemainsDetailService.get_remains_detail_data(accounting_code)
        
        return {
            'found': True,
            'name': name,
            'nomenclature_kd': first_result.nomenclature_kd,
            'article': accounting_code,
            'title': getattr(first_result, 'name', name),
            'required': required,
            'quantity': 0,
            'project': None,
            'status_color': 'gray',
            'base_unit': detail_data.get('base_unit', 'шт') if detail_data else 'шт',
            'total_available': detail_data.get('total_quantity', 0) if detail_data else 0,
            'sufficient': False,
            'error': f'Материал не найден на проектах: {projects}',
            'available_projects': [p['project'] for p in detail_data.get('details_any_projects', [])] if detail_data else []
        }
    
    def process_with_projects(self, input_file, projects, start_row=2, end_row=None, output_folder=None):
        """
        Обработка Excel файла с проверкой материалов на проектах
        
        Args:
            input_file: путь к исходному файлу
            projects: список проектов (может быть как список строк, так и список словарей с ключом 'project')
            start_row: начальная строка (столбец 2 - наименование, столбец 6 - количество)
            end_row: конечная строка
            output_folder: папка для сохранения результата
        
        Returns:
            str: путь к созданному файлу с результатами
        """
        print(f"\n{'='*60}")
        print(f"📊 ОБРАБОТКА EXCEL ФАЙЛА")
        print(f"{'='*60}")
        print(f"📁 Файл: {input_file}")
        print(f"📋 Диапазон строк: {start_row} - {end_row if end_row else 'до конца'}")
        
        # Преобразуем проекты в список строк, если пришли словари
        project_names = []
        if projects and len(projects) > 0:
            if isinstance(projects[0], dict):
                # Если проекты пришли как словари, извлекаем поле 'project'
                project_names = [p.get('project', str(p)) for p in projects]
            else:
                # Если уже строки, используем как есть
                project_names = [str(p) for p in projects]
        
        print(f"📋 Проекты для проверки: {project_names}")
        
        # Сбрасываем счетчики
        self.materials_found = 0
        self.materials_not_found = 0
        self.materials_insufficient = 0
        
        # Проверяем существование файла
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Файл не найден: {input_file}")
        
        # Открываем исходный файл
        try:
            wb = openpyxl.load_workbook(input_file, data_only=True)
            sheet = wb.active
            print(f"📋 Активный лист: {sheet.title}")
            print(f"📋 Всего строк в листе: {sheet.max_row}")
        except Exception as e:
            raise Exception(f"Ошибка при открытии Excel файла: {e}")
        
        # Собираем данные из указанных столбцов в заданном диапазоне
        materials_data = []
        empty_names = 0
        empty_required = 0
        
        # Определяем конечную строку
        max_row = sheet.max_row
        if end_row is None or end_row > max_row:
            end_row = max_row
            print(f"📋 Скорректирована конечная строка до: {end_row}")
        
        # Проверяем корректность диапазона
        if start_row < 1:
            start_row = 1
            print("⚠️ Начальная строка скорректирована до 1")
        
        if start_row > end_row:
            raise ValueError(f"Начальная строка ({start_row}) больше конечной ({end_row})")
        
        # Читаем данные
        print(f"\n📖 Чтение данных из файла...")
        for row_idx in range(start_row, end_row + 1):
            # Столбец 2 (B) - наименование материала
            name_cell = sheet.cell(row=row_idx, column=2)
            # Столбец 6 (F) - требуемое количество
            required_cell = sheet.cell(row=row_idx, column=6)
            
            name_value = str(name_cell.value).strip() if name_cell.value else ""
            required_value = required_cell.value if required_cell.value else 0
            
            # Пытаемся преобразовать required в число
            try:
                required_value = float(required_value) if required_value else 0
            except (ValueError, TypeError):
                required_value = 0
            
            if name_value:
                materials_data.append({
                    'row': row_idx,
                    'name': name_value,
                    'required': required_value,
                    'original_name': name_cell.value,
                    'original_required': required_cell.value
                })
            else:
                empty_names += 1
            
            if not required_value:
                empty_required += 1
        
        self.last_row_count = len(materials_data)
        self.processed_range = f"{start_row}-{end_row}"
        
        print(f"\n📊 Статистика чтения:")
        print(f"📋 Найдено материалов: {len(materials_data)}")
        print(f"📋 Пустых наименований: {empty_names}")
        print(f"📋 Нулевых требований: {empty_required}")
        
        if len(materials_data) == 0:
            print("⚠️ В указанном диапазоне нет данных!")
        
        # Проверяем каждый материал
        print(f"\n🔍 Проверка материалов на проектах...")
        results = []
        
        for i, material in enumerate(materials_data, 1):
            print(f"\r   Прогресс: {i}/{len(materials_data)}", end="")
            
            result = self.check_material_availability(
                name=material['name'],
                required=material['required'],
                projects=project_names  # Используем список названий проектов
            )
            
            if result:
                # Обновляем счетчики
                if not result.get('found', False):
                    self.materials_not_found += 1
                elif result.get('sufficient', False):
                    self.materials_found += 1
                else:
                    self.materials_insufficient += 1
                
                # Добавляем информацию о строке
                result['row'] = material['row']
                result['original_name'] = material['original_name']
                result['original_required'] = material['original_required']
                
                results.append(result)
        
        print(f"\n\n✅ Проверка завершена")
        
        # Создаем новый файл с результатами
        result_wb = openpyxl.Workbook()
        result_sheet = result_wb.active
        result_sheet.title = "Результаты проверки"
        
        # ============================================
        # ЗАГОЛОВКИ ТАБЛИЦЫ РЕЗУЛЬТАТОВ
        # ============================================
        headers = [
            "№", "Строка", "Наименование (исходное)", "Требуется",
            "Статус", "Артикул", "Наименование (найденное)",
            "Проект", "Доступно", "Ед. изм.", "Достаточно",
            "Всего на проекте", "Партии"
        ]
        
        for col, header in enumerate(headers, 1):
            cell = result_sheet.cell(row=1, column=col, value=header)
            cell.font = openpyxl.styles.Font(bold=True)
            cell.fill = openpyxl.styles.PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            cell.font = openpyxl.styles.Font(color="FFFFFF", bold=True)
        
        # ============================================
        # ЗАПОЛНЯЕМ РЕЗУЛЬТАТЫ
        # ============================================
        for i, result in enumerate(results, 1):
            # Определяем статус и цвет
            if not result.get('found', False):
                status = "❌ Не найден"
                status_color = "FF0000"  # Красный
            elif result.get('sufficient', False):
                status = "✅ Достаточно"
                status_color = "00FF00"  # Зеленый
            else:
                status = "⚠️ Недостаточно"
                status_color = "FFFF00"  # Желтый
            
            row_data = [
                i,  # №
                result.get('row', ''),  # Строка
                result.get('original_name', ''),  # Наименование (исходное)
                result.get('required', ''),  # Требуется
                status,  # Статус
                result.get('article', ''),  # Артикул
                result.get('title', ''),  # Наименование (найденное)
                result.get('project', 'Не найден'),  # Проект
                result.get('quantity', 0),  # Доступно
                result.get('base_unit', ''),  # Ед. изм.
                "Да" if result.get('sufficient', False) else "Нет",  # Достаточно
                result.get('total_available', 0),  # Всего на проекте
                ", ".join(result.get('party', [])) if result.get('party') else ""  # Партии
            ]
            
            for col, value in enumerate(row_data, 1):
                cell = result_sheet.cell(row=i+1, column=col, value=value)
                
                # Красим строку в зависимости от статуса
                if col == 5:  # Столбец со статусом
                    cell.fill = openpyxl.styles.PatternFill(start_color=status_color, end_color=status_color, fill_type="solid")
        
        # ============================================
        # ИНФОРМАЦИЯ ОБ ОБРАБОТКЕ
        # ============================================
        info_row = len(results) + 3
        
        result_sheet.cell(row=info_row, column=1, value="📊 ИНФОРМАЦИЯ ОБ ОБРАБОТКЕ")
        result_sheet.cell(row=info_row, column=1).font = openpyxl.styles.Font(bold=True, size=12)
        info_row += 1
        
        # Основная информация
        info_data = [
            f"📁 Исходный файл: {os.path.basename(input_file)}",
            f"📄 Диапазон строк: {start_row}-{end_row}",
            f"📊 Обработано материалов: {len(materials_data)}",
            f"✅ Найдено с достаточным количеством: {self.materials_found}",
            f"⚠️ Найдено с недостаточным количеством: {self.materials_insufficient}",
            f"❌ Не найдено в базе: {self.materials_not_found}",
            f"📋 Проекты для проверки: {', '.join(project_names)}",
            f"🕒 Дата обработки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ]
        
        for info in info_data:
            result_sheet.cell(row=info_row, column=1, value=info)
            info_row += 1
        
        # ============================================
        # СОЗДАЕМ ОТДЕЛЬНЫЙ ЛИСТ С ПРОЕКТАМИ
        # ============================================
        projects_sheet = result_wb.create_sheet("Проекты")
        
        projects_sheet.cell(row=1, column=1, value="№")
        projects_sheet.cell(row=1, column=2, value="Проект")
        
        for i, project in enumerate(project_names, 1):
            projects_sheet.cell(row=i+1, column=1, value=i)
            projects_sheet.cell(row=i+1, column=2, value=project)
        
        # Если проекты пришли как словари, добавляем дополнительную информацию
        if projects and len(projects) > 0 and isinstance(projects[0], dict):
            # Добавляем колонки для дополнительных данных
            projects_sheet.cell(row=1, column=3, value="ID")
            projects_sheet.cell(row=1, column=4, value="Статус")
            
            for i, project in enumerate(projects, 1):
                projects_sheet.cell(row=i+1, column=3, value=project.get('id', ''))
                projects_sheet.cell(row=i+1, column=4, value=project.get('status_color', 'gray'))
        
        # ============================================
        # НАСТРАИВАЕМ ШИРИНУ КОЛОНОК
        # ============================================
        for sheet in [result_sheet, projects_sheet]:
            for col in sheet.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                sheet.column_dimensions[column].width = adjusted_width
        
        # ============================================
        # СОХРАНЯЕМ ФАЙЛ
        # ============================================
        if output_folder is None:
            output_folder = os.path.dirname(input_file)
        
        base_name = os.path.basename(input_file)
        name_without_ext = os.path.splitext(base_name)[0]
        
        result_filename = f"{name_without_ext}_проверка_строк_{start_row}-{end_row}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        result_path = os.path.join(output_folder, result_filename)
        
        result_wb.save(result_path)
        
        print(f"\n{'='*60}")
        print(f"💾 РЕЗУЛЬТАТ СОХРАНЕН:")
        print(f"📁 {result_path}")
        print(f"{'='*60}")
        print(f"\n📊 ИТОГИ ПРОВЕРКИ:")
        print(f"✅ Достаточно: {self.materials_found}")
        print(f"⚠️ Недостаточно: {self.materials_insufficient}")
        print(f"❌ Не найдено: {self.materials_not_found}")
        print(f"📋 Всего обработано: {len(materials_data)}")
        
        return result_path