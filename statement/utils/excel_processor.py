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
        Проверяет доступность материала на проектах с учетом приоритета
        
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
        
        # Получаем ВСЕ результаты поиска
        all_matches = list(search_results)
        
        # Перебираем проекты по приоритету (сначала важные)
        for project_name in projects:
            # Перебираем все найденные артикулы
            for match in all_matches:
                accounting_code = getattr(match, 'accounting_code', None)
                if not accounting_code:
                    continue
                
                # Проверяем этот артикул на текущем проекте
                result = RemainsDetailService.get_total_quantity_by_article_and_project(
                    article=accounting_code,
                    project_name=project_name
                )
                
                # Если артикул есть на этом проекте
                if result and result.get('total_quantity', 0) > 0:
                    quantity = result['total_quantity']
                    
                    return {
                        'found': True,
                        'name': name,
                        'nomenclature_kd': getattr(match, 'nomenclature_kd', ''),
                        'article': result['article'],
                        'title': result.get('title', getattr(match, 'name', name)),
                        'required': required,
                        'quantity': quantity,
                        'project': result['project'],
                        'status_color': result.get('status_color', 'gray'),
                        'base_unit': result.get('base_unit', 'шт'),
                        'total_available': result.get('total_quantity', 0),
                        'sufficient': quantity >= required,
                        'positions_details': result.get('positions_details', [])
                    }
        
        # Если ни один артикул не найден ни на одном проекте
        first_match = all_matches[0]
        return {
            'found': True,
            'name': name,
            'nomenclature_kd': getattr(first_match, 'nomenclature_kd', ''),
            'article': getattr(first_match, 'accounting_code', ''),
            'title': getattr(first_match, 'name', name),
            'required': required,
            'quantity': 0,
            'project': None,
            'status_color': 'gray',
            'base_unit': 'шт',
            'total_available': 0,
            'sufficient': False,
            'positions_details': [],
            'error': f'Материал не найден на проектах: {projects}'
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
        
        print(f"📋 Проекты для проверки (по приоритету): {project_names}")
        
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
                projects=project_names
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
        # ЗАГОЛОВКИ ТАБЛИЦЫ РЕЗУЛЬТАТОВ (БЕЗ СТОЛБЦА "№")
        # ============================================
        headers = [
            "Строка",                      # 1. Номер строки в исходном файле
            "Наименование (исходное)",     # 2. Исходное наименование из файла
            "Код",                         # 3. Артикул (код материала)
            "Наименование (найденное)",    # 4. Найденное наименование из базы
            "Ед. изм.",                    # 5. Единица измерения
            "Требуется",                   # 6. Требуемое количество
            "Всего на проекте",            # 7. Доступное количество на проекте
            "Проект",                      # 8. Проект, с которого берем
            "Статус",                      # 9. Статус (Достаточно/Недостаточно/Не найден)
            "Партии"                       # 10. Список партий (только номера)
        ]

        # Создаем заголовки
        for col, header in enumerate(headers, 1):
            cell = result_sheet.cell(row=1, column=col, value=header)
            cell.font = openpyxl.styles.Font(bold=True)
            cell.fill = openpyxl.styles.PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            cell.font = openpyxl.styles.Font(color="FFFFFF", bold=True)

        # ============================================
        # ЗАПОЛНЯЕМ РЕЗУЛЬТАТЫ (БЕЗ СТОЛБЦА "№")
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
            
            # Формируем строку с партиями (только номера, без количества)
            parties_str = ""
            if result.get('positions_details'):
                parties_list = [p['party'] for p in result['positions_details']]
                parties_str = ", ".join(parties_list)
            
            row_data = [
                result.get('row', ''),                      # 1. Строка
                result.get('original_name', ''),            # 2. Наименование (исходное)
                result.get('article', ''),                  # 3. Код
                result.get('title', ''),                    # 4. Наименование (найденное)
                result.get('base_unit', ''),                # 5. Ед. изм.
                result.get('required', ''),                 # 6. Требуется
                result.get('quantity', 0),                  # 7. Всего на проекте
                result.get('project', 'Не найден'),         # 8. Проект
                status,                                     # 9. Статус
                parties_str                                 # 10. Партии
            ]
            
            for col, value in enumerate(row_data, 1):
                cell = result_sheet.cell(row=i+1, column=col, value=value)
                
                # Красим строку в зависимости от статуса
                if col == 9:  # Столбец со статусом (теперь 9-й)
                    cell.fill = openpyxl.styles.PatternFill(start_color=status_color, end_color=status_color, fill_type="solid")

        # ============================================
        # НАСТРАИВАЕМ ШИРИНУ КОЛОНОК
        # ============================================
        column_widths = {
            1: 8,   # Строка
            2: 35,  # Наименование (исходное)
            3: 15,  # Код
            4: 35,  # Наименование (найденное)
            5: 8,   # Ед. изм.
            6: 12,  # Требуется
            7: 15,  # Всего на проекте
            8: 20,  # Проект
            9: 15,  # Статус
            10: 35  # Партии
        }

        for col, width in column_widths.items():
            result_sheet.column_dimensions[openpyxl.utils.get_column_letter(col)].width = width
                
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
            f"📋 Проекты для проверки (по приоритету): {', '.join(project_names)}",
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
        projects_sheet.cell(row=1, column=3, value="Приоритет")
        
        for i, project in enumerate(project_names, 1):
            projects_sheet.cell(row=i+1, column=1, value=i)
            projects_sheet.cell(row=i+1, column=2, value=project)
            projects_sheet.cell(row=i+1, column=3, value=i)
        
        # Если проекты пришли как словари, добавляем дополнительную информацию
        if projects and len(projects) > 0 and isinstance(projects[0], dict):
            # Добавляем колонки для дополнительных данных
            projects_sheet.cell(row=1, column=4, value="ID")
            projects_sheet.cell(row=1, column=5, value="Статус")
            
            for i, project in enumerate(projects, 1):
                projects_sheet.cell(row=i+1, column=4, value=project.get('id', ''))
                projects_sheet.cell(row=i+1, column=5, value=project.get('status_color', 'gray'))
        
        # Настраиваем ширину колонок для листа проектов
        projects_sheet.column_dimensions['A'].width = 5
        projects_sheet.column_dimensions['B'].width = 25
        projects_sheet.column_dimensions['C'].width = 10
        projects_sheet.column_dimensions['D'].width = 10
        projects_sheet.column_dimensions['E'].width = 10
        
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