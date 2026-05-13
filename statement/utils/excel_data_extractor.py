# statement/utils/excel_data_extractor.py

import pandas as pd
import logging
from typing import Dict, List, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class ExcelDataExtractor:
    """
    Класс для извлечения данных из Excel файлов для AccountingData
    """
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None
        
    def load_file(self):
        """Загружает Excel файл"""
        try:
            file_ext = Path(self.file_path).suffix.lower()
            
            if file_ext in ['.xlsx', '.xlsm']:
                self.df = pd.read_excel(self.file_path, engine='openpyxl', header=None)
            elif file_ext == '.xls':
                self.df = pd.read_excel(self.file_path, engine='xlrd', header=None)
            else:
                raise ValueError(f"Неподдерживаемый формат файла: {file_ext}")
            
            logger.info(f"✅ Загружен файл: {self.file_path}, строк: {len(self.df)}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки файла: {e}")
            raise
    
    def detect_columns(self) -> Dict[str, str]:
        """
        Определяет колонки для файлов с известной структурой
        """
        if self.df is None:
            raise ValueError("Файл не загружен. Вызовите load_file() сначала")
        
        # Для ваших файлов структура обычно такая:
        # Колонка 0: пустая или № п/п
        # Колонка 1: Наименование
        # Колонка 2: На 1 изд.
        # Колонка 3: Код
        # Колонка 4: Артикул
        # Колонка 5: Требуется
        # и т.д.
        
        column_mapping = {
            'accounting_code': 3,      # Код - колонка D (индекс 3)
            'nomenclature_kd': 1,      # Наименование - колонка B (индекс 1)
            'accounting_name': 4,      # Артикул - колонка E (индекс 4)
            '_header_row': 6           # Строка с заголовками (7-я строка, индекс 6)
        }
        
        # Проверяем, есть ли данные в предполагаемых колонках
        sample_row = None
        for idx in range(min(20, len(self.df))):
            row = self.df.iloc[idx]
            # Проверяем, есть ли в колонке 3 что-то похожее на код
            val = str(row[3]) if 3 < len(row) and pd.notna(row[3]) else ''
            if val and any(c.isdigit() for c in val):
                sample_row = idx
                break
        
        if sample_row is not None:
            column_mapping['_data_start_row'] = sample_row
            logger.info(f"Данные начинаются со строки {sample_row + 1}")
        else:
            column_mapping['_data_start_row'] = 10  # По умолчанию с 11 строки
        
        logger.info(f"Используем колонки: Код={column_mapping['accounting_code']}, "
                    f"Наименование={column_mapping['nomenclature_kd']}, "
                    f"Артикул={column_mapping['accounting_name']}")
        
        return column_mapping
    

    # statement/utils/excel_data_extractor.py - обновленный метод extract_data

    def extract_data(self, column_mapping: Dict[str, str] = None, start_row: int = 11) -> List[Dict[str, Any]]:
        """
        Извлекает данные из Excel начиная с указанной строки
        """
        if self.df is None:
            raise ValueError("Файл не загружен. Вызовите load_file() сначала")
        
        if column_mapping is None:
            column_mapping = self.detect_columns()
        
        # Используем start_row из параметра или из column_mapping
        data_start_row = column_mapping.get('_data_start_row', start_row - 1)
        
        if data_start_row >= len(self.df):
            logger.warning(f"Строка начала {data_start_row + 1} больше чем строк в файле ({len(self.df)})")
            return []
        
        df_data = self.df.iloc[data_start_row:]
        
        extracted_data = []
        skipped_rows = 0
        invalid_code_rows = 0
        
        code_col = column_mapping['accounting_code']
        name_col = column_mapping['nomenclature_kd']
        article_col = column_mapping['accounting_name']
        
        logger.info(f"Извлекаем данные: строки с {data_start_row + 1} по {len(self.df)}, "
                    f"колонки: код={code_col}, наименование={name_col}, артикул={article_col}")
        
        for idx, row in df_data.iterrows():
            try:
                # Получаем значения
                code_val = row[code_col] if code_col < len(row) else None
                name_val = row[name_col] if name_col < len(row) else None
                article_val = row[article_col] if article_col < len(row) else None
                
                # Преобразуем в строки и очищаем
                code = str(code_val).strip() if pd.notna(code_val) else ''
                name = str(name_val).strip() if pd.notna(name_val) else ''
                article = str(article_val).strip() if pd.notna(article_val) else ''
                
                # Пропускаем пустые строки
                if not code and not name:
                    skipped_rows += 1
                    continue
                
                # ВАЛИДАЦИЯ accounting_code
                is_valid_code = False
                
                # Проверяем: должен начинаться с "Б0" и длина не более 9 символов
                if code and code.startswith('Б0') and len(code) <= 9:
                    is_valid_code = True
                else:
                    # Если код не подходит, проверяем другие колонки
                    # Может быть код в колонке с артикулом?
                    if article and article.startswith('Б0') and len(article) <= 9:
                        code = article
                        is_valid_code = True
                        logger.debug(f"Строка {idx + 2}: код найден в колонке артикула: {code}")
                    
                    # Или может быть наименование содержит код?
                    elif name and 'Б0' in name:
                        # Пробуем извлечь код из наименования
                        import re
                        match = re.search(r'Б0\d{1,7}', name)
                        if match:
                            code = match.group()
                            is_valid_code = True
                            logger.debug(f"Строка {idx + 2}: код извлечен из наименования: {code}")
                
                if not is_valid_code:
                    invalid_code_rows += 1
                    logger.debug(f"Строка {idx + 2}: пропущена - некорректный код '{code}' (должен начинаться с Б0 и быть <= 9 символов)")
                    continue
                
                # Очищаем от лишних символов
                code = code.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').replace('"', '').replace("'", "")
                name = name.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').replace('"', '').replace("'", "")
                article = article.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').replace('"', '').replace("'", "")
                
                extracted_data.append({
                    'accounting_code': code,
                    'nomenclature_kd': name if name else article,
                    'accounting_name': article,
                    'row_number': idx + 2
                })
                
                # Логируем первые 10 записей для отладки
                if len(extracted_data) <= 10:
                    logger.info(f"  ✅ Строка {idx + 2}: код='{code}', наименование='{name[:50]}...', артикул='{article}'")
                
            except Exception as e:
                logger.warning(f"Ошибка обработки строки {idx + 2}: {e}")
                skipped_rows += 1
        
        logger.info(f"✅ Извлечено {len(extracted_data)} записей "
                    f"(пропущено пустых: {skipped_rows}, "
                    f"некорректный код: {invalid_code_rows})")
        return extracted_data