# excel_processor.py
import os
import openpyxl
import pandas as pd
import time
import re
from datetime import datetime
from typing import List, Dict, Optional, Union, Tuple

from finder.utils.services.details_service import RemainsDetailService
from statement.utils.comparison_search_service import SearchService


class ExcelProcessor:
    """
    Обработчик Excel файлов с проверкой доступности материалов на проектах
    Поддерживает форматы .xlsx и .xls
    Динамическое определение столбцов и строки начала данных по порядковому номеру
    Сохраняет исходную нумерацию строк
    """
    
    def __init__(self):
        self.last_row_count = 0
        self.processed_range = None
        self.materials_found = 0
        self.materials_not_found = 0
        self.materials_insufficient = 0
        self.debug = True
        self.timeout_seconds = 30
        
        # Маппинг названий столбцов (ключевые слова для поиска)
        self.column_mapping = {
            'row_number': ['№', '№ п/п', '№ пп', 'Номер', '№ строки', 'п/п', '№п/п', '№ п.п'],
            'name': ['Материальные ценности', 'Наименование', 'Материал', 'Наименование материала', 'Номенклатура'],
            'code': ['Код', 'Код материала', 'Код номенклатуры', 'Артикул КД', 'КД'],
            'article': ['Артикул', 'Артикул складской', 'Складской артикул', 'Артикул СКЛАД'],
            'required': ['На 1 изд.', 'Требуется', 'Количество', 'Норма расхода', 'Потребность', 'На изв.']
        }
    
    def _log(self, message):
        """Логирование с временем"""
        if self.debug:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def _read_excel_file(self, file_path: str):
        """Универсальное чтение Excel файла"""
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
    
    def _find_header_row(self, sheet, max_rows=20):
        """
        Находит строку с заголовками, сканируя первые N строк
        
        Returns:
            tuple: (header_row_index, detected_columns)
        """
        self._log(f"🔍 Поиск строки с заголовками (первые {max_rows} строк)...")
        
        for row_idx in range(1, min(max_rows, sheet.max_row) + 1):
            found_columns = {}
            for col_idx in range(1, min(sheet.max_column, 20)):
                cell_value = sheet.cell(row=row_idx, column=col_idx).value
                if cell_value:
                    cell_lower = str(cell_value).strip().lower()
                    
                    for col_type, keywords in self.column_mapping.items():
                        for keyword in keywords:
                            if keyword.lower() in cell_lower:
                                found_columns[col_type] = col_idx
                                self._log(f"  Найден столбец '{col_type}' в колонке {col_idx}: '{cell_value}'")
                                break
            
            if len(found_columns) >= 3:
                self._log(f"✅ Найдена строка заголовков: строка {row_idx}")
                self._log(f"   Определенные столбцы: {found_columns}")
                return row_idx, found_columns
        
        self._log(f"⚠️ Строка заголовков не найдена, использую значения по умолчанию")
        default_columns = {
            'row_number': 1,
            'name': 2,
            'code': 3,
            'article': 4,
            'required': 5
        }
        return 1, default_columns
    
    def _find_data_start_row_by_row_number(self, sheet, header_row, row_number_col) -> int:
        """
        Находит строку, с которой начинаются данные, по порядковому номеру
        Ищет первую строку после заголовков, где в колонке row_number_col есть число 1
        
        Returns:
            int: номер строки с которой начинаются данные
        """
        self._log(f"🔍 Поиск строки начала данных по порядковому номеру (колонка {row_number_col})...")
        
        start_search = header_row + 1
        end_search = min(header_row + 500, sheet.max_row)
        
        for row_idx in range(start_search, end_search + 1):
            cell_value = sheet.cell(row=row_idx, column=row_number_col).value
            
            if cell_value is None:
                continue
            
            try:
                num_value = int(float(str(cell_value).strip()))
                if num_value == 1:
                    self._log(f"✅ Найдена строка начала данных: строка {row_idx} (порядковый номер = {num_value})")
                    return row_idx
                elif num_value > 1 and row_idx == start_search:
                    self._log(f"✅ Найдена строка начала данных: строка {row_idx} (порядковый номер = {num_value})")
                    return row_idx
            except (ValueError, TypeError):
                continue
            
            cell_str = str(cell_value).strip()
            if cell_str.isdigit() and int(cell_str) == 1:
                self._log(f"✅ Найдена строка начала данных: строка {row_idx} (порядковый номер = {cell_str})")
                return row_idx
        
        self._log(f"⚠️ Не удалось найти строку по порядковому номеру, использую поиск по наличию данных")
        return self._find_data_start_row_by_content(sheet, header_row)
    
    def _find_data_start_row_by_content(self, sheet, header_row) -> int:
        """Находит строку, с которой начинаются данные, по наличию данных в ячейках (старый метод)"""
        data_start = header_row + 1
        
        for row_idx in range(header_row + 1, min(header_row + 100, sheet.max_row + 1)):
            has_data = False
            for col_idx in range(1, min(sheet.max_column, 10)):
                cell_value = sheet.cell(row=row_idx, column=col_idx).value
                if cell_value and str(cell_value).strip():
                    has_data = True
                    break
            
            if has_data:
                data_start = row_idx
                break
        
        self._log(f"📋 Данные начинаются с строки: {data_start}")
        return data_start
    
    def _get_column_value(self, sheet, row_idx, col_idx, col_type):
        """Получает значение из ячейки с преобразованием"""
        if col_idx is None:
            return None
        
        cell = sheet.cell(row=row_idx, column=col_idx)
        value = cell.value
        
        if col_type in ['row_number', 'required']:
            if value is None:
                return 0
            try:
                if col_type == 'row_number':
                    return int(float(str(value).strip())) if str(value).strip().isdigit() else 0
                return float(value) if '.' in str(value) else int(value)
            except (ValueError, TypeError):
                return 0
        
        if value is None:
            return ""
        return str(value).strip()
    
    def check_material_availability(self, name: str, required: Union[int, float], projects: List[str], index: int, total: int, original_article: str = None) -> Optional[Dict]:
        """
        Проверяет доступность материала на проектах с учетом приоритета
        """
        self._log(f"  [{index}/{total}] Проверка: '{name[:50]}...' (требуется: {required})")
        
        start_time = time.time()
        
        try:
            if original_article:
                self._log(f"    Поиск по артикулу: {original_article}")
                from finder.models import Nomenclature
                try:
                    nomenclature = Nomenclature.objects.filter(accounting_code=original_article).first()
                    if nomenclature:
                        all_matches = [nomenclature]
                        self._log(f"    Найден артикул: {original_article}")
                    else:
                        all_matches = list(SearchService.search_by_nomenclature(name))
                except:
                    all_matches = list(SearchService.search_by_nomenclature(name))
            else:
                self._log(f"    Поиск в базе по наименованию...")
                search_results = SearchService.search_by_nomenclature(name)
                
                if not search_results.exists():
                    self._log(f"    ❌ Материал не найден в базе")
                    return {
                        'found': False,
                        'name': name,
                        'required': required,
                        'article': original_article or '',
                        'error': 'Материал не найден в базе'
                    }
                
                all_matches = list(search_results)
            
            self._log(f"    Найдено артикулов: {len(all_matches)}")
            
            for project_idx, project_name in enumerate(projects, 1):
                for match_idx, match in enumerate(all_matches, 1):
                    accounting_code = getattr(match, 'accounting_code', None)
                    if not accounting_code:
                        continue
                    
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
                                'original_article': original_article,
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
            
            first_match = all_matches[0] if all_matches else None
            elapsed = time.time() - start_time
            self._log(f"    ⚠️ Материал не найден на проектах, время: {elapsed:.2f} сек")
            
            return {
                'found': True,
                'name': name,
                'nomenclature_kd': getattr(first_match, 'nomenclature_kd', '') if first_match else '',
                'article': getattr(first_match, 'accounting_code', original_article or ''),
                'original_article': original_article,
                'title': getattr(first_match, 'name', name) if first_match else name,
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
                'article': original_article or '',
                'error': f'Ошибка при проверке: {str(e)}'
            }
    
    def process_with_projects(self, input_file, projects, start_row=None, end_row=None, output_folder=None):
        """
        Обработка Excel файла с проверкой материалов на проектах
        Динамическое определение столбцов и строки начала данных по порядковому номеру
        Сохраняет исходную нумерацию строк
        """
        print(f"\n{'='*60}")
        print(f"📊 ОБРАБОТКА EXCEL ФАЙЛА")
        print(f"{'='*60}")
        print(f"📁 Файл: {input_file}")
        
        file_ext = os.path.splitext(input_file)[1].lower()
        print(f"📁 Формат файла: {file_ext}")
        
        # Преобразуем проекты в список строк
        project_names = []
        if projects and len(projects) > 0:
            if isinstance(projects[0], dict):
                project_names = [p.get('project', str(p)) for p in projects]
            else:
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
            wb, sheet, is_xlsx = self._read_excel_file(input_file)
            print(f"📋 Активный лист: {sheet.title}")
            print(f"📋 Всего строк в листе: {sheet.max_row}")
            
            # Определяем строку с заголовками
            header_row, detected_columns = self._find_header_row(sheet)
            print(f"📋 Строка заголовков: {header_row}")
            
            # Определяем столбцы
            name_col = detected_columns.get('name')
            required_col = detected_columns.get('required')
            code_col = detected_columns.get('code')
            article_col = detected_columns.get('article')
            row_num_col = detected_columns.get('row_number')
            
            if not name_col:
                name_col = 2
                print(f"⚠️ Столбец 'Наименование' не найден, использую колонку {name_col}")
            else:
                print(f"✅ Столбец 'Наименование' - колонка {name_col}")
            
            if not required_col:
                required_col = 5
                print(f"⚠️ Столбец 'Требуется' не найден, использую колонку {required_col}")
            else:
                print(f"✅ Столбец 'Требуется' - колонка {required_col}")
            
            if code_col:
                print(f"✅ Столбец 'Код' - колонка {code_col}")
            if article_col:
                print(f"✅ Столбец 'Артикул' - колонка {article_col}")
            if row_num_col:
                print(f"✅ Столбец '№ п/п' - колонка {row_num_col}")
            
        except Exception as e:
            raise Exception(f"Ошибка при открытии Excel файла: {e}")
        
        # ============================================
        # ОПРЕДЕЛЕНИЕ СТРОКИ НАЧАЛА ДАННЫХ
        # ============================================
        data_start_row = header_row + 1
        
        if row_num_col:
            data_start_row = self._find_data_start_row_by_row_number(sheet, header_row, row_num_col)
        else:
            data_start_row = self._find_data_start_row_by_content(sheet, header_row)
        
        # Корректируем start_row если он передан
        if start_row is None:
            start_row = data_start_row
        elif start_row < data_start_row:
            print(f"⚠️ Начальная строка {start_row} меньше строки данных {data_start_row}, корректирую")
            start_row = data_start_row
        
        print(f"📋 Диапазон строк: {start_row} - {end_row if end_row else 'до конца'}")
        
        # Собираем данные
        materials_data = []
        empty_names = 0
        empty_required = 0
        
        max_row = sheet.max_row
        if end_row is None or end_row > max_row:
            end_row = max_row
        
        if start_row > end_row:
            raise ValueError(f"Начальная строка ({start_row}) больше конечной ({end_row})")
        
        print(f"\n📖 Чтение данных из файла...")
        
        for row_idx in range(start_row, end_row + 1):
            name_value = self._get_column_value(sheet, row_idx, name_col, 'name')
            required_value = self._get_column_value(sheet, row_idx, required_col, 'required')
            code_value = self._get_column_value(sheet, row_idx, code_col, 'code') if code_col else None
            article_value = self._get_column_value(sheet, row_idx, article_col, 'article') if article_col else None
            
            # Получаем исходный номер строки из файла (есть колонка с номерами или используем реальный номер строки)
            if row_num_col:
                original_row_number = self._get_column_value(sheet, row_idx, row_num_col, 'row_number')
            else:
                original_row_number = row_idx - data_start_row + 1  # Нумеруем с 1 от начала данных
            
            if row_idx <= start_row + 5:
                print(f"   Строка {row_idx}: №={original_row_number}, Наименование='{name_value[:50] if name_value else ''}...', Требуется={required_value}, Артикул={article_value}")
            
            if name_value and name_value.strip():
                materials_data.append({
                    'row': row_idx,                          # Реальный номер строки в Excel
                    'original_row_number': original_row_number,  # Исходный номер из колонки № п/п
                    'name': name_value,
                    'required': required_value if required_value and required_value > 0 else 0,
                    'original_name': sheet.cell(row=row_idx, column=name_col).value if name_col else None,
                    'original_required': sheet.cell(row=row_idx, column=required_col).value if required_col else None,
                    'code': code_value,
                    'article': article_value
                })
            else:
                empty_names += 1
            
            if not required_value or required_value == 0:
                empty_required += 1
        
        self.last_row_count = len(materials_data)
        
        # Формируем строку диапазона для отображения
        if start_row == data_start_row and end_row == max_row:
            self.processed_range = f"автоопределение (строки {start_row}-{end_row})"
        else:
            self.processed_range = f"{start_row}-{end_row if end_row else 'конец'}"
        
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
            print(f"🔍 Материал {i}/{len(materials_data)} (№ строки: {material.get('original_row_number', material['row'])})")
            print(f"{'='*50}")
            
            original_article = material.get('article') or material.get('code')
            
            result = self.check_material_availability(
                name=material['name'],
                required=material['required'],
                projects=project_names,
                index=i,
                total=len(materials_data),
                original_article=original_article
            )
            
            if result:
                if not result.get('found', False):
                    self.materials_not_found += 1
                elif result.get('sufficient', False):
                    self.materials_found += 1
                else:
                    self.materials_insufficient += 1
                
                # Добавляем информацию о строке (сохраняем исходный номер)
                result['row'] = material['row']
                result['original_row_number'] = material.get('original_row_number', i)
                result['original_name'] = material['original_name']
                result['original_required'] = material['original_required']
                result['code'] = material.get('code')
                result['original_article'] = material.get('article')
                
                results.append(result)
                
                print(f"\n📊 Промежуточный итог:")
                print(f"   ✅ Достаточно: {self.materials_found}")
                print(f"   ⚠️ Недостаточно: {self.materials_insufficient}")
                print(f"   ❌ Не найдено: {self.materials_not_found}")
        
        print(f"\n\n✅ Проверка завершена!")
        

        # ============================================
        # СОЗДАЕМ РЕЗУЛЬТИРУЮЩИЙ ФАЙЛ
        # ============================================
        result_wb = openpyxl.Workbook()
        result_sheet = result_wb.active
        result_sheet.title = "Результаты проверки"

        # Заголовки
        headers = [
            "№ строки",
            "Строка в файле",
            "Наименование (исходное)",
            "Код",
            "Наименование (найденное)",
            "Ед. изм.",
            "Требуется",
            "Всего на проекте",
            "Проект",
            "Статус",
            "Партии"
        ]

        # Создаем заголовки
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
            
            article_to_display = result.get('article', '')
            if not article_to_display and result.get('original_article'):
                article_to_display = result.get('original_article')
            
            row_data = [
                result.get('original_row_number', i),
                result.get('row', ''),
                result.get('original_name', ''),
                article_to_display,
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
                if col == 10:
                    cell.fill = openpyxl.styles.PatternFill(start_color=status_color, end_color=status_color, fill_type="solid")

        # Настраиваем ширину колонок
        column_widths = {
            1: 10,  # № строки
            2: 12,  # Строка в файле
            3: 35,  # Наименование (исходное)
            4: 15,  # Код
            5: 35,  # Наименование (найденное)
            6: 8,   # Ед. изм.
            7: 12,  # Требуется
            8: 15,  # Всего на проекте
            9: 20,  # Проект
            10: 15, # Статус
            11: 35  # Партии
        }

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
            f"📋 Строка заголовков: {header_row}",
            f"📋 Строка начала данных (определена): {data_start_row}",
            f"📋 Столбцы: Наименование={name_col}, Требуется={required_col}, Артикул={article_col}, № п/п={row_num_col}",
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

        # Создаем отдельный лист с информацией о проектах
        projects_sheet = result_wb.create_sheet("Проекты")

        projects_sheet.cell(row=1, column=1, value="№")
        projects_sheet.cell(row=1, column=2, value="Проект")
        projects_sheet.cell(row=1, column=3, value="Приоритет")

        for i, project in enumerate(project_names, 1):
            projects_sheet.cell(row=i+1, column=1, value=i)
            projects_sheet.cell(row=i+1, column=2, value=project)
            projects_sheet.cell(row=i+1, column=3, value=i)

        projects_sheet.column_dimensions['A'].width = 5
        projects_sheet.column_dimensions['B'].width = 25
        projects_sheet.column_dimensions['C'].width = 10

        # ============================================
        # СОХРАНЯЕМ ФАЙЛ С БЕЗОПАСНЫМ ИМЕНЕМ
        # ============================================
        if output_folder is None:
            output_folder = os.path.dirname(input_file)

        # Создаем безопасное имя файла (без специальных символов)
        base_name = os.path.basename(input_file)
        name_without_ext = os.path.splitext(base_name)[0]

        # Очищаем имя файла от проблемных символов
        import re
        safe_name = re.sub(r'[^\w\-а-яА-Я]', '_', name_without_ext)
        safe_name = re.sub(r'_+', '_', safe_name)  # Убираем множественные подчеркивания
        safe_name = safe_name[:100]  # Ограничиваем длину

        result_filename = f"{safe_name}_проверка_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        result_path = os.path.join(output_folder, result_filename)

        # Убеждаемся, что папка существует
        os.makedirs(output_folder, exist_ok=True)

        try:
            result_wb.save(result_path)
            print(f"✅ Файл сохранен: {result_path}")
        except Exception as e:
            print(f"❌ Ошибка сохранения файла: {e}")
            # Пробуем сохранить с еще более коротким именем
            fallback_name = f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            result_path = os.path.join(output_folder, fallback_name)
            result_wb.save(result_path)
            print(f"✅ Файл сохранен с именем по умолчанию: {result_path}")

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