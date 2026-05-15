# statement/tasks.py

from celery import shared_task
from datetime import datetime
from typing import Dict, Any
import logging
import os
import shutil
from .utils.accounting_validator import AccountingDataValidator

from .models import SMBFileIndex, ProcessedFileLog, SMBPathConfig
from .utils.excel_data_extractor import ExcelDataExtractor
from .utils.smb import SmbFolderVk
from config import settings
from django.utils import timezone
import os


logger = logging.getLogger(__name__)


# ============================================
# ОСНОВНАЯ ЗАДАЧА ИНДЕКСАЦИИ (для всех типов конфигураций)
# ============================================
@shared_task(bind=True, name='statement.tasks.index_smb_files_all')
def index_smb_files(self, config_id: int = None, force: bool = False) -> Dict[str, Any]:
    """
    Индексация SMB файлов для указанной конфигурации
    """
    logger.info(f"🔄 Запущена индексация для config_id={config_id}, force={force}")
    
    from .models import SMBPathConfig
    
    result = {
        'success': False,
        'configs_processed': [],
        'errors': []
    }
    
    try:
        if config_id:
            config = SMBPathConfig.objects.filter(id=config_id, is_active=True).first()
            if not config:
                raise ValueError(f"Конфигурация {config_id} не найдена")
            
            from .utils.smb_indexer import SMBFileIndexer
            indexer = SMBFileIndexer(config)
            stats = indexer.scan_and_index(force_rescan=force)
            
            result['configs_processed'].append({
                'config_id': config.id,
                'config_name': config.name,
                'stats': stats
            })
            result['success'] = True
        else:
            # Индексация всех активных конфигураций
            from .utils.smb_indexer import index_all_active_configs
            full_result = index_all_active_configs(force_rescan=force)
            result = full_result
        
        result['finished_at'] = datetime.now().isoformat()
        
    except Exception as e:
        logger.error(f"❌ Ошибка индексации: {e}")
        result['error'] = str(e)
        result['success'] = False
    
    return result


# ============================================
# ЗАДАЧА ДЛЯ ИНДЕКСАЦИИ ТОЛЬКО ПОИСКОВЫХ КОНФИГУРАЦИЙ (Новые ведомости)
# ============================================
@shared_task(name='statement.tasks.index_search_files')
def index_search_files(force: bool = False) -> Dict[str, Any]:
    """
    Индексация файлов для поиска ВК (незаполненные ведомости)
    """
    logger.info("🔄 Индексация файлов для ПОИСКА ВК")
    
    from .utils.smb_indexer import index_configs_by_type
    result = index_configs_by_type(config_type='search', force_rescan=force)
    
    return result


# ============================================
# ЗАДАЧА ДЛЯ ИНДЕКСАЦИИ ТОЛЬКО ACCOUNTING SOURCE (Готовые ведомости)
# ============================================
@shared_task(name='statement.tasks.index_accounting_source')
def index_accounting_source(force: bool = False) -> Dict[str, Any]:
    """
    Индексация файлов для пополнения AccountingData (готовые ведомости)
    """
    logger.info("🔄 Индексация файлов для ACCOUNTING DATA")
    
    from .utils.smb_indexer import index_configs_by_type
    result = index_configs_by_type(config_type='accounting_source', force_rescan=force)
    
    return result



# ============================================
# ЗАДАЧА ДЛЯ ПОПОЛНЕНИЯ ACCOUNTING DATA (чтение индекса заполненных ведомостей)
# ============================================

@shared_task(name='statement.tasks.populate_accounting_data')
def populate_accounting_data(config_id: int = None, limit: int = None) -> Dict[str, Any]:
    """
    Пополнение базы AccountingData из готовых ведомостей
    """
    logger.info(f"🚀 Запуск пополнения AccountingData: config_id={config_id}, limit={limit}")
    
    
    # Получаем конфигурации типа accounting_source
    if config_id:
        configs = SMBPathConfig.objects.filter(id=config_id, config_type='accounting_source', is_active=True)
    else:
        configs = SMBPathConfig.objects.filter(is_active=True, config_type='accounting_source')
    
    if not configs.exists():
        return {
            'success': False,
            'error': 'Нет активных конфигураций типа accounting_source'
        }
    
    # Получаем файлы для обработки
    queryset = SMBFileIndex.objects.filter(
        config__in=configs,
        is_available=True,
        processing_status='pending'
    ).select_related('config').order_by('created_at')
    
    if limit:
        queryset = queryset[:limit]
    
    total_files = queryset.count()
    logger.info(f"📋 Найдено файлов для обработки: {total_files}")
    
    stats = {
        'success': True,
        'total': total_files,
        'processed': 0,
        'errors': 0,
        'rows_imported': 0,
        'invalid_rows': 0,
        'details': []
    }
    
    for file_index in queryset:
        work_folder = None
        file_result = {
            'file_id': file_index.id,
            'filename': file_index.filename,
            'success': False,
            'rows_imported': 0,
            'invalid_rows': 0,
            'error': None
        }
        
        try:
            logger.info(f"=" * 60)
            logger.info(f"📥 Начинаем обработку файла: {file_index.filename}")
            logger.info(f"   ID файла: {file_index.id}")
            logger.info(f"   Путь в индексе: {file_index.file_path}")
            
            # Отмечаем файл как обрабатываемый
            file_index.processing_status = 'processing'
            file_index.save(update_fields=['processing_status'])
            
            # Создаем рабочую папку
            work_root = os.path.join(settings.BASE_DIR, 'work_accounting')
            os.makedirs(work_root, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_filename = file_index.filename.replace('.xlsx', '').replace('.xls', '').replace(' ', '_')
            work_folder = os.path.join(work_root, f"{safe_filename}_{timestamp}")
            os.makedirs(work_folder, exist_ok=True)
            
            logger.info(f"📁 Рабочая папка: {work_folder}")
            
            # Подключаемся к SMB
            config = file_index.config
            logger.info(f"🔧 Конфигурация: {config.name}")
            logger.info(f"   Путь поиска: {config.search_path}")
            
            # Парсим путь для подключения
            path_parts = config.search_path.strip('\\').split('\\')
            logger.info(f"   Разбор пути: {path_parts}")
            
            if len(path_parts) >= 2:
                smb_server = path_parts[0]
                smb_share = path_parts[1]
                logger.info(f"   SMB сервер: {smb_server}")
                logger.info(f"   SMB шара: {smb_share}")
            else:
                raise ValueError(f"Некорректный путь: {config.search_path}")
            
            # Используем путь из индекса для скачивания
            remote_file_path = file_index.file_path
            logger.info(f"📡 Полный путь к файлу на SMB: {remote_file_path}")
            
            # Создаем SMB клиент
            smb = SmbFolderVk(server=smb_server, share=smb_share)
            
            # Проверяем существование файла перед скачиванием
            if not smb.file_exists(remote_file_path):
                raise FileNotFoundError(f"Файл не найден на SMB по пути: {remote_file_path}")
            
            # Скачиваем файл
            local_file_path = os.path.join(work_folder, file_index.filename)
            logger.info(f"📥 Скачиваем файл...")
            
            smb.download_file(remote_file_path, work_folder)
            
            # Проверяем, что файл скачался
            if not os.path.exists(local_file_path):
                raise FileNotFoundError(f"Файл не скачался: {local_file_path}")
            
            file_size = os.path.getsize(local_file_path)
            logger.info(f"✅ Файл скачан успешно, размер: {file_size} байт")
            
            # Извлекаем данные из Excel
            logger.info(f"📊 Начинаем извлечение данных из Excel...")
            extractor = ExcelDataExtractor(local_file_path)
            extractor.load_file()
            
            # Определяем колонки
            column_mapping = extractor.detect_columns()
            logger.info(f"📊 Определены колонки: {column_mapping}")
            
            # Извлекаем данные, начиная с 11 строки
            data = extractor.extract_data(column_mapping, start_row=11)
            
            if not data:
                logger.warning(f"⚠️ Не удалось извлечь данные из файла {file_index.filename}")
                raise ValueError("Не удалось извлечь данные из файла (нет данных или неверные колонки)")
            
            logger.info(f"📊 Извлечено {len(data)} записей из файла, начинаем валидацию...")
            
            # Сохраняем в AccountingData через валидатор
            validation_stats = AccountingDataValidator.save_to_database(data)
            
            # Обновляем статистику
            rows_imported = validation_stats['created'] + validation_stats['updated']
            stats['rows_imported'] += rows_imported
            stats['invalid_rows'] += validation_stats['invalid']
            
            # Логируем результаты валидации
            logger.info(f"✅ Результаты валидации файла {file_index.filename}:")
            logger.info(f"   Всего строк: {validation_stats['total']}")
            logger.info(f"   Валидных: {validation_stats['valid']}")
            logger.info(f"   Невалидных: {validation_stats['invalid']}")
            logger.info(f"   Создано новых: {validation_stats['created']}")
            logger.info(f"   Обновлено: {validation_stats['updated']}")
            
            # Если есть ошибки, логируем их
            if validation_stats['errors']:
                logger.warning(f"   Ошибки/пропуски ({len(validation_stats['errors'])}):")
                for err in validation_stats['errors'][:10]:  # Показываем первые 10 ошибок
                    logger.warning(f"     - {err}")
            
            # Если не было ни одной валидной строки, считаем обработку неуспешной
            if validation_stats['valid'] == 0:
                raise ValueError(f"Не найдено ни одной валидной строки в файле. Пропущено: {validation_stats['invalid']}")
            
            # Отмечаем файл как обработанный
            file_index.processing_status = 'processed'
            file_index.processed_at = timezone.now()
            file_index.save(update_fields=['processing_status', 'processed_at'])
            
            # Создаем лог с детализацией
            ProcessedFileLog.objects.create(
                file_index=file_index,
                rows_processed=rows_imported,
                status='processed',
                error_message=f"Валидных: {validation_stats['valid']}, Невалидных: {validation_stats['invalid']}, Создано: {validation_stats['created']}, Обновлено: {validation_stats['updated']}"
            )
            
            stats['processed'] += 1
            file_result['success'] = True
            file_result['rows_imported'] = rows_imported
            file_result['invalid_rows'] = validation_stats['invalid']
            file_result['validation_stats'] = {
                'total': validation_stats['total'],
                'valid': validation_stats['valid'],
                'invalid': validation_stats['invalid'],
                'created': validation_stats['created'],
                'updated': validation_stats['updated']
            }
            
            logger.info(f"✅ Обработан: {file_index.filename}, импортировано {rows_imported} записей, пропущено {validation_stats['invalid']}")
            
        except Exception as e:
            stats['errors'] += 1
            file_result['error'] = str(e)
            
            logger.error(f"❌ Ошибка {file_index.filename}: {e}", exc_info=True)
            
            try:
                file_index.processing_status = 'error'
                file_index.processing_error = str(e)[:500]
                file_index.save(update_fields=['processing_status', 'processing_error'])
                
                ProcessedFileLog.objects.create(
                    file_index=file_index,
                    status='error',
                    error_message=str(e)[:500]
                )
            except Exception as log_error:
                logger.error(f"Ошибка при сохранении лога: {log_error}")
        
        finally:
            stats['details'].append(file_result)
            # Очищаем временную папку
            if work_folder and os.path.exists(work_folder):
                try:
                    shutil.rmtree(work_folder)
                    logger.info(f"🧹 Удалена временная папка: {work_folder}")
                except Exception as e:
                    logger.warning(f"⚠️ Не удалось удалить папку {work_folder}: {e}")
    
    # Итоговая статистика
    logger.info(f"🎉 Пополнение AccountingData завершено:")
    logger.info(f"   Обработано файлов: {stats['processed']}")
    logger.info(f"   Ошибок: {stats['errors']}")
    logger.info(f"   Импортировано записей: {stats['rows_imported']}")
    logger.info(f"   Пропущено невалидных записей: {stats['invalid_rows']}")
    
    return stats


# ============================================
# ЗАДАЧА ДЛЯ ОБРАБОТКИ ФАЙЛОВ (общая)
# ============================================
@shared_task(name='statement.tasks.process_smb_files')
def process_smb_files(config_id: int = None, limit: int = None) -> Dict[str, Any]:
    """
    Обработка непрочитанных файлов (перенаправляет в populate_accounting_data)
    """
    return populate_accounting_data(config_id=config_id, limit=limit)


# ============================================
# АЛИАСЫ ДЛЯ ОБРАТНОЙ СОВМЕСТИМОСТИ
# ============================================
index_search_files = index_search_files
index_accounting_source = index_accounting_source
populate_accounting_data = populate_accounting_data
process_smb_files = process_smb_files