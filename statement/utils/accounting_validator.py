# statement/utils/accounting_validator.py

import logging
from typing import Dict, List, Any, Tuple
from django.core.exceptions import ValidationError
from finder.models import AccountingData

logger = logging.getLogger(__name__)


class AccountingDataValidator:
    """
    Валидатор и сервис для сохранения данных в AccountingData
    """
    
    # Паттерны для исключения номенклатуры КД
    SKIP_PATTERNS = ['Б00', 'Б000', 'Б0000', 'C00', 'C000', 'C0000']
    
    @classmethod
    def should_skip_nomenclature(cls, nomenclature_kd: str) -> bool:
        """
        Проверяет, нужно ли пропустить номенклатуру КД
        Возвращает True, если номенклатура начинается с паттернов:
        Б00, Б000, С00, С000 (в любом регистре)
        """
        if not nomenclature_kd:
            return True
        
        # Приводим к верхнему регистру для сравнения
        nomenclature_upper = nomenclature_kd.strip().upper()
        
        # Проверяем, начинается ли строка с любого из паттернов
        for pattern in cls.SKIP_PATTERNS:
            if nomenclature_upper.startswith(pattern):
                logger.debug(f"Пропуск: номенклатура КД '{nomenclature_kd}' начинается с '{pattern}'")
                return True
        
        return False
    
    @classmethod
    def is_complete_row(cls, accounting_code: str, nomenclature_kd: str, accounting_name: str) -> bool:
        """
        Проверяет, что все поля строки заполнены
        """
        if not accounting_code or not accounting_code.strip():
            logger.debug(f"Пропуск: пустой accounting_code")
            return False
        
        if not nomenclature_kd or not nomenclature_kd.strip():
            logger.debug(f"Пропуск: пустой nomenclature_kd для кода {accounting_code}")
            return False
        
        if not accounting_name or not accounting_name.strip():
            logger.debug(f"Пропуск: пустой accounting_name для кода {accounting_code}")
            return False
        
        return True
    
    @classmethod
    def is_duplicate(cls, accounting_code: str, nomenclature_kd: str, accounting_name: str) -> bool:
        """
        Проверяет, существует ли уже такой экземпляр в базе
        Дублем считается полное совпадение всех трех полей
        """
        exists = AccountingData.objects.filter(
            accounting_code=accounting_code,
            nomenclature_kd=nomenclature_kd,
            accounting_name=accounting_name
        ).exists()
        
        if exists:
            logger.debug(f"Найден дубль: код={accounting_code}, номенклатура={nomenclature_kd}, наименование={accounting_name}")
        
        return exists
    
    @classmethod
    def validate_and_prepare(cls, item: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
        """
        Полная валидация одной строки данных
        
        Returns:
            Tuple[is_valid, data_dict, error_message]
        """
        accounting_code = item.get('accounting_code', '').strip()
        nomenclature_kd = item.get('nomenclature_kd', '').strip()
        accounting_name = item.get('accounting_name', '').strip()
        row_number = item.get('row_number', 0)
        
        # Проверка 1: Все поля должны быть заполнены
        if not cls.is_complete_row(accounting_code, nomenclature_kd, accounting_name):
            return False, {}, f"Строка {row_number}: не все поля заполнены"
        
        # Проверка 2: Проверка кода accounting_code (должен начинаться с Б0 и не длиннее 9 символов)
        if not accounting_code.startswith('Б0'):
            return False, {}, f"Строка {row_number}: код '{accounting_code}' должен начинаться с 'Б0'"
        
        if len(accounting_code) > 9:
            return False, {}, f"Строка {row_number}: код '{accounting_code}' слишком длинный (макс. 9 символов)"
        
        # Проверка 3: Проверка номенклатуры на исключения
        if cls.should_skip_nomenclature(nomenclature_kd):
            return False, {}, f"Строка {row_number}: номенклатура '{nomenclature_kd}' исключена (начинается с Б00/С00)"
        
        # Проверка 4: Проверка на дубликаты
        if cls.is_duplicate(accounting_code, nomenclature_kd, accounting_name):
            return False, {}, f"Строка {row_number}: дубликат (код={accounting_code}, номенклатура={nomenclature_kd})"
        
        return True, {
            'accounting_code': accounting_code,
            'nomenclature_kd': nomenclature_kd,
            'accounting_name': accounting_name
        }, ""
    
    @classmethod
    def save_to_database(cls, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Сохраняет данные в AccountingData с валидацией
        
        Returns:
            Dict со статистикой сохранения
        """
        stats = {
            'total': len(data),
            'valid': 0,
            'invalid': 0,
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': [],
            'skipped_rows': []
        }
        
        for item in data:
            is_valid, validated_data, error_msg = cls.validate_and_prepare(item)
            
            if not is_valid:
                stats['invalid'] += 1
                stats['skipped'] += 1
                stats['errors'].append(error_msg)
                stats['skipped_rows'].append({
                    'row': item.get('row_number', 0),
                    'error': error_msg,
                    'data': item
                })
                continue
            
            stats['valid'] += 1
            
            try:
                # Используем update_or_create с уникальными полями
                # Дубль уже исключен на уровне валидации, но на всякий случай
                obj, created = AccountingData.objects.update_or_create(
                    accounting_code=validated_data['accounting_code'],
                    nomenclature_kd=validated_data['nomenclature_kd'],
                    defaults={
                        'accounting_name': validated_data['accounting_name']
                    }
                )
                
                if created:
                    stats['created'] += 1
                    logger.debug(f"Создана запись: {validated_data['accounting_code']} - {validated_data['nomenclature_kd']}")
                else:
                    stats['updated'] += 1
                    logger.debug(f"Обновлена запись: {validated_data['accounting_code']} - {validated_data['nomenclature_kd']}")
                    
            except Exception as e:
                stats['invalid'] += 1
                stats['skipped'] += 1
                stats['errors'].append(f"Ошибка БД: {str(e)}")
                logger.error(f"Ошибка при сохранении {validated_data['accounting_code']}: {e}")
        
        logger.info(f"Статистика сохранения: обработано {stats['total']}, "
                   f"валидных {stats['valid']}, невалидных {stats['invalid']}, "
                   f"создано {stats['created']}, обновлено {stats['updated']}")
        
        if stats['errors']:
            logger.warning(f"Ошибки: {stats['errors'][:5]}")  # Показываем первые 5 ошибок
        
        return stats