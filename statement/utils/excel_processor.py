# excel_processor.py
import os
import openpyxl
import pandas as pd
import time
import signal
from datetime import datetime
from typing import List, Dict, Optional, Union

from finder.utils.services.details_service import RemainsDetailService
from statement.utils.comparison_search_service import SearchService


class ExcelProcessor:
    """
    Обработчик Excel файлов с проверкой доступности материалов на проектах
    Поддерживает форматы .xlsx и .xls
    """
    
    def __init__(self):
        self.last_row_count = 0
        self.processed_range = None
        self.materials_found = 0
        self.materials_not_found = 0
        self.materials_insufficient = 0
        self.debug = True
        self.timeout_seconds = 30  # Таймаут на один материал
    
    def _log(self, message):
        """Логирование с временем"""
        if self.debug:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def _read_excel_file(self, file_path: str):
        """
        Универсальное чтение Excel файла (поддерживает .xlsx и .xls)
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.xlsx':
            wb = openpyxl.load_workbook(file_path, data_only=True)
            sheet = wb.active
            return wb, sheet, True
        elif file_ext == '.xls':
            try:
                self._log(f"Чтение .xls файла через pandas...")
                df = pd.read_excel(file_path, engine='xlrd', header=None)
                
                wb = openpyxl.Workbook()
                sheet = wb.active
                
                for row_idx, row in df.iterrows():
                    for col_idx, value in enumerate(row, 1):
                        if pd.notna(value):
                            sheet.cell(row=row_idx + 1, column=col_idx, value=value)
                
                self._log(f"Успешно прочитано {len(df)} строк")
                return wb, sheet, False
            except Exception as e:
                raise Exception(f"Ошибка при чтении .xls файла: {e}")
        else:
            raise Exception(f"Неподдерживаемый формат файла: {file_ext}")
    
    def check_material_availability(self, name: str, required: Union[int, float], projects: List[str], index: int, total: int) -> Optional[Dict]:
        """
        Проверяет доступность материала на проектах с учетом приоритета
        С добавлением таймаута и отладки
        """
        self._log(f"  [{index}/{total}] Проверка: '{name[:50]}...' (требуется: {required})")
        
        start_time = time.time()
        
        try:
            # Поиск в базе по наименованию
            self._log(f"    Поиск в базе...")
            search_results = SearchService.search_by_nomenclature(name)
            
            if not search_results.exists():
                self._log(f"    ❌ Материал не найден в базе")
                return {
                    'found': False,
                    'name': name,
                    'required': required,
                    'error': 'Материал не найден в базе'
                }
            
            # Получаем ВСЕ результаты поиска
            all_matches = list(search_results)
            self._log(f"    Найдено артикулов: {len(all_matches)}")
            
            # Перебираем проекты по приоритету
            for project_idx, project_name in enumerate(projects, 1):
                self._log(f"    Проверка проекта {project_idx}/{len(projects)}: {project_name}")
                
                # Перебираем все найденные артикулы
                for match_idx, match in enumerate(all_matches, 1):
                    accounting_code = getattr(match, 'accounting_code', None)
                    if not accounting_code:
                        continue
                    
                    # Проверяем артикул на проекте
                    try:
                        result = RemainsDetailService.get_total_quantity_by_article_and_project(
                            article=accounting_code,
                            project_name=project_name
                        )
                        
                        if result and result.get('total_quantity', 0) > 0:
                            quantity = result['total_quantity']
                            elapsed = time.time() - start_time
                            self._log(f"    ✅ Найден на проекте {project_name}: {accounting_code} (доступно: {quantity}) за {elapsed:.2f} сек")
                            
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
                    except Exception as e:
                        self._log(f"    ⚠️ Ошибка при проверке артикула {accounting_code}: {e}")
                        continue
            
            # Если ни один артикул не найден
            first_match = all_matches[0]
            elapsed = time.time() - start_time
            self._log(f"    ⚠️ Материал не найден на проектах, время: {elapsed:.2f} сек")
            
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
            
        except Exception as e:
            elapsed = time.time() - start_time
            self._log(f"    ❌ ОШИБКА при проверке: {e}, время: {elapsed:.2f} сек")
            return {
                'found': False,
                'name': name,
                'required': required,
                'error': f'Ошибка при проверке: {str(e)}'
            }
    
    def process_with_projects(self, input_file, projects, start_row=2, end_row=None, output_folder=None):
        """
        Обработка Excel файла с проверкой материалов на проектах
        """
        print(f"\n{'='*60}")
        print(f"📊 ОБРАБОТКА EXCEL ФАЙЛА")
        print(f"{'='*60}")
        print(f"📁 Файл: {input_file}")
        
        file_ext = os.path.splitext(input_file)[1].lower()
        print(f"📁 Формат файла: {file_ext}")
        print(f"📋 Диапазон строк: {start_row} - {end_row if end_row else 'до конца'}")
        
        # Преобразуем проекты в список строк
        project_names = []
        if projects and len(projects) > 0:
            if isinstance(projects[0], dict):
                project_names = [p.get('project', str(p)) for p in projects]
            else:
                project_names = [str(p) for p in projects]
        
        print(f"📋 Проекты для проверки (по приоритету): {project_names}")
        print(f"📋 Всего проектов: {len(project_names)}")
        
        # Сбрасываем счетчики
        self.materials_found = 0
        self.materials_not_found = 0
        self.materials_insufficient = 0
        
        # Проверяем существование файла
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Файл не найден: {input_file}")
        
        # Открываем исходный файл
        try:
            wb, sheet, is_xlsx = self._read_excel_file(input_file)
            print(f"📋 Активный лист: {sheet.title}")
            print(f"📋 Всего строк в листе: {sheet.max_row}")
        except Exception as e:
            raise Exception(f"Ошибка при открытии Excel файла: {e}")
        
        # Собираем данные
        materials_data = []
        empty_names = 0
        empty_required = 0
        
        max_row = sheet.max_row
        if end_row is None or end_row > max_row:
            end_row = max_row
        
        if start_row < 1:
            start_row = 1
        
        if start_row > end_row:
            raise ValueError(f"Начальная строка ({start_row}) больше конечной ({end_row})")
        
        print(f"\n📖 Чтение данных из файла...")
        for row_idx in range(start_row, end_row + 1):
            name_cell = sheet.cell(row=row_idx, column=2)
            required_cell = sheet.cell(row=row_idx, column=6)
            
            name_value = str(name_cell.value).strip() if name_cell.value else ""
            required_value = required_cell.value if required_cell.value else 0
            
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
            return None
        
        # Проверяем каждый материал
        print(f"\n🔍 Проверка материалов на проектах...")
        print(f"⏱️ Это может занять время (до {self.timeout_seconds} сек на материал)")
        print(f"📊 Всего материалов: {len(materials_data)}")
        print("-" * 50)
        
        results = []
        
        for i, material in enumerate(materials_data, 1):
            print(f"\n{'='*50}")
            print(f"🔍 Материал {i}/{len(materials_data)}")
            print(f"{'='*50}")
            
            result = self.check_material_availability(
                name=material['name'],
                required=material['required'],
                projects=project_names,
                index=i,
                total=len(materials_data)
            )
            
            if result:
                if not result.get('found', False):
                    self.materials_not_found += 1
                elif result.get('sufficient', False):
                    self.materials_found += 1
                else:
                    self.materials_insufficient += 1
                
                result['row'] = material['row']
                result['original_name'] = material['original_name']
                result['original_required'] = material['original_required']
                
                results.append(result)
                
                # Показываем промежуточный итог
                print(f"\n📊 Промежуточный итог:")
                print(f"   ✅ Достаточно: {self.materials_found}")
                print(f"   ⚠️ Недостаточно: {self.materials_insufficient}")
                print(f"   ❌ Не найдено: {self.materials_not_found}")
        
        print(f"\n\n✅ Проверка завершена!")
        print(f"📊 ИТОГИ ПРОВЕРКИ:")
        print(f"✅ Достаточно: {self.materials_found}")
        print(f"⚠️ Недостаточно: {self.materials_insufficient}")
        print(f"❌ Не найдено: {self.materials_not_found}")
        
        # Создаем результирующий файл (как в вашем коде)
        result_wb = openpyxl.Workbook()
        result_sheet = result_wb.active
        result_sheet.title = "Результаты проверки"
        
        # Заголовки
        headers = [
            "Строка", "Наименование (исходное)", "Код", "Наименование (найденное)",
            "Ед. изм.", "Требуется", "Всего на проекте", "Проект", "Статус", "Партии"
        ]
        
        for col, header in enumerate(headers, 1):
            cell = result_sheet.cell(row=1, column=col, value=header)
            cell.font = openpyxl.styles.Font(bold=True)
            cell.fill = openpyxl.styles.PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            cell.font = openpyxl.styles.Font(color="FFFFFF", bold=True)
        
        # Заполняем результаты
        for i, result in enumerate(results, 1):
            if not result.get('found', False):
                status = "❌ Не найден"
                status_color = "FF0000"
            elif result.get('sufficient', False):
                status = "✅ Достаточно"
                status_color = "00FF00"
            else:
                status = "⚠️ Недостаточно"
                status_color = "FFFF00"
            
            parties_str = ""
            if result.get('positions_details'):
                parties_list = [p['party'] for p in result['positions_details']]
                parties_str = ", ".join(parties_list)
            
            row_data = [
                result.get('row', ''),
                result.get('original_name', ''),
                result.get('article', ''),
                result.get('title', ''),
                result.get('base_unit', ''),
                result.get('required', ''),
                result.get('quantity', 0),
                result.get('project', 'Не найден'),
                status,
                parties_str
            ]
            
            for col, value in enumerate(row_data, 1):
                cell = result_sheet.cell(row=i+1, column=col, value=value)
                if col == 9:
                    cell.fill = openpyxl.styles.PatternFill(start_color=status_color, end_color=status_color, fill_type="solid")
        
        # Настройка ширины колонок
        column_widths = {1: 8, 2: 35, 3: 15, 4: 35, 5: 8, 6: 12, 7: 15, 8: 20, 9: 15, 10: 35}
        for col, width in column_widths.items():
            result_sheet.column_dimensions[openpyxl.utils.get_column_letter(col)].width = width
        
        # Информация об обработке
        info_row = len(results) + 3
        result_sheet.cell(row=info_row, column=1, value="📊 ИНФОРМАЦИЯ ОБ ОБРАБОТКЕ")
        result_sheet.cell(row=info_row, column=1).font = openpyxl.styles.Font(bold=True, size=12)
        info_row += 1
        
        info_data = [
            f"📁 Исходный файл: {os.path.basename(input_file)}",
            f"📄 Формат файла: {file_ext}",
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
        
        # Сохраняем файл
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
        
        return result_path