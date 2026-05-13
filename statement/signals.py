# statement/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import SMBPathConfig
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=SMBPathConfig)
def config_updated(sender, instance, created, **kwargs):
    """При создании или изменении конфигурации очищаем кэш"""
    cache.delete('active_smb_config')
    logger.info(f"Конфигурация SMB обновлена: {instance.name}")
    
    # Если конфигурация новая и активная, запускаем индексацию
    if created and instance.is_active:
        from .tasks import index_smb_files
        from django.db import transaction
        
        def run_indexing():
            try:
                index_smb_files.delay(config_id=instance.id, force=False)
                logger.info(f"Запущена автоматическая индексация для новой конфигурации: {instance.name}")
            except Exception as e:
                logger.error(f"Ошибка при запуске индексации: {e}")
        
        transaction.on_commit(run_indexing)


@receiver(post_delete, sender=SMBPathConfig)
def config_deleted(sender, instance, **kwargs):
    """При удалении конфигурации очищаем кэш"""
    cache.delete('active_smb_config')
    logger.info(f"Конфигурация SMB удалена: {instance.name}")