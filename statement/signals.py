# statement/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import SMBPathConfig, SMBIndexSchedule
from .scheduler import update_smb_indexing_schedule
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=SMBIndexSchedule)
def schedule_updated(sender, instance, created, **kwargs):
    """При изменении расписания обновляем Celery Beat"""
    logger.info(f"Расписание индексации обновлено: {instance}")
    # Используем on_commit для выполнения после фиксации транзакции
    from django.db import transaction
    transaction.on_commit(update_smb_indexing_schedule)


@receiver(post_save, sender=SMBPathConfig)
def config_updated(sender, instance, created, **kwargs):
    """При создании или изменении конфигурации очищаем кэш"""
    cache.delete('active_smb_config')
    logger.info(f"Конфигурация SMB обновлена: {instance.name}")
    
    # Если конфигурация новая и активная, можно запустить индексацию
    if created and instance.is_active:
        from .tasks import index_smb_files
        # Запускаем индексацию асинхронно через 5 секунд
        from django.db import transaction
        transaction.on_commit(
            lambda: index_smb_files.delay(config_id=instance.id, force=False)
        )
        logger.info(f"Запущена автоматическая индексация для новой конфигурации: {instance.name}")


@receiver(post_delete, sender=SMBPathConfig)
def config_deleted(sender, instance, **kwargs):
    """При удалении конфигурации очищаем кэш"""
    cache.delete('active_smb_config')
    logger.info(f"Конфигурация SMB удалена: {instance.name}")