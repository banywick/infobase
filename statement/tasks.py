# statement/tasks.py
from celery import shared_task
from celery.schedules import crontab
from django.core.cache import cache
from datetime import datetime
from typing import Dict, Any
import logging

from .models import SMBPathConfig
from .utils.smb_indexer import SMBFileIndexer, index_all_active_configs

logger = logging.getLogger(__name__)


@shared_task(bind=True, name='statement.tasks.index_smb_files')
def index_smb_files(self, config_id: int = None, force: bool = False) -> Dict[str, Any]:
    """
    Задача индексации SMB файлов
    
    Args:
        config_id: ID конфигурации (если None, то индексируются все активные)
        force: Принудительное полное сканирование
    """
    task_id = self.request.id
    logger.info(f"🔄 Запущена задача индексации {task_id}")
    
    # Обновляем статус в кэше для отслеживания прогресса
    cache.set(f'smb_index_task_{task_id}', {
        'status': 'running',
        'started_at': datetime.now().isoformat(),
        'current_config': None,
        'progress': 0,
        'total_files': 0,
        'processed_files': 0
    }, timeout=3600)  # Храним 1 час
    
    result = {
        'task_id': task_id,
        'success': False,
        'configs_processed': [],
        'errors': [],
        'total_files': 0,
        'started_at': datetime.now().isoformat()
    }
    
    try:
        if config_id:
            # Индексация конкретной конфигурации
            config = SMBPathConfig.objects.filter(id=config_id, is_active=True).first()
            if not config:
                raise ValueError(f"Конфигурация с ID {config_id} не найдена или неактивна")
            
            cache.set(f'smb_index_task_{task_id}', {
                **cache.get(f'smb_index_task_{task_id}'),
                'current_config': config.name
            }, timeout=3600)
            
            indexer = SMBFileIndexer(config)
            stats = indexer.scan_and_index(force_rescan=force)
            
            result['configs_processed'].append({
                'config_id': config.id,
                'config_name': config.name,
                'stats': stats
            })
            result['total_files'] += stats.get('total_found', 0)
            result['success'] = True
            
        else:
            # Индексация всех активных конфигураций
            active_configs = SMBPathConfig.objects.filter(is_active=True)
            
            if not active_configs.exists():
                raise ValueError("Нет активных конфигураций для индексации")
            
            total_configs = active_configs.count()
            for idx, config in enumerate(active_configs):
                logger.info(f"📁 Индексация конфигурации {idx+1}/{total_configs}: {config.name}")
                
                # Обновляем статус
                cache.set(f'smb_index_task_{task_id}', {
                    **cache.get(f'smb_index_task_{task_id}'),
                    'current_config': config.name,
                    'progress': int((idx / total_configs) * 100)
                }, timeout=3600)
                
                try:
                    indexer = SMBFileIndexer(config)
                    stats = indexer.scan_and_index(force_rescan=force)
                    
                    result['configs_processed'].append({
                        'config_id': config.id,
                        'config_name': config.name,
                        'stats': stats
                    })
                    result['total_files'] += stats.get('total_found', 0)
                    
                except Exception as e:
                    error_msg = f"Ошибка при индексации {config.name}: {str(e)}"
                    logger.error(error_msg)
                    result['errors'].append(error_msg)
            
            result['success'] = len(result['configs_processed']) > 0
        
        result['finished_at'] = datetime.now().isoformat()
        result['duration'] = (datetime.fromisoformat(result['finished_at']) - 
                             datetime.fromisoformat(result['started_at'])).total_seconds()
        
        # Обновляем финальный статус
        cache.set(f'smb_index_task_{task_id}', {
            'status': 'completed' if result['success'] else 'failed',
            'finished_at': result['finished_at'],
            'result': result
        }, timeout=3600)
        
        logger.info(f"✅ Задача индексации завершена: {result['total_files']} файлов")
        
    except Exception as e:
        logger.error(f"❌ Ошибка в задаче индексации: {e}")
        result['error'] = str(e)
        result['success'] = False
        
        cache.set(f'smb_index_task_{task_id}', {
            'status': 'failed',
            'error': str(e),
            'finished_at': datetime.now().isoformat()
        }, timeout=3600)
    
    return result


@shared_task
def check_smb_files_availability():
    """
    Периодическая задача для проверки доступности файлов в индексе
    Отмечает файлы, которые были удалены
    """
    from .models import SMBFileIndex
    
    logger.info("🔍 Проверка доступности SMB файлов")
    
    # Получаем все активные конфигурации
    configs = SMBPathConfig.objects.filter(is_active=True)
    
    checked_count = 0
    unavailable_count = 0
    
    for config in configs:
        try:
            indexer = SMBFileIndexer(config)
            
            # Проверяем первые 100 файлов из индекса
            files_to_check = SMBFileIndex.objects.filter(
                config=config,
                is_available=True
            )[:100]
            
            for file_index in files_to_check:
                checked_count += 1
                try:
                    # Пытаемся получить информацию о файле
                    stat_result = indexer.smb.stat_file(file_index.file_path)
                    if not stat_result:
                        file_index.is_available = False
                        file_index.save()
                        unavailable_count += 1
                except Exception:
                    file_index.is_available = False
                    file_index.save()
                    unavailable_count += 1
                    
        except Exception as e:
            logger.error(f"Ошибка при проверке конфигурации {config.name}: {e}")
    
    logger.info(f"✅ Проверка завершена. Проверено: {checked_count}, отмечено недоступных: {unavailable_count}")
    
    return {
        'checked': checked_count,
        'marked_unavailable': unavailable_count
    }


@shared_task
def refresh_smb_index():
    """
    Полное обновление индекса (вызывается по расписанию)
    """
    logger.info("🔄 Плановое обновление SMB индекса")
    return index_smb_files(force=False)


# # Если нужно добавить задачу с расписанием прямо здесь
# @periodic_task(
#     run_every=crontab(hour=2, minute=0),  # Каждый день в 2:00
#     name="scheduled_smb_indexing"
# )
def scheduled_smb_indexing():
    """
    Плановая индексация SMB файлов
    """
    return refresh_smb_index()