# statement/scheduler.py
from celery import current_app
from celery.schedules import crontab
from django.conf import settings
from .models import SMBIndexSchedule
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


def update_smb_indexing_schedule():
    """
    Обновляет расписание индексации в Celery Beat
    """
    try:
        schedule_config = SMBIndexSchedule.objects.first()
        
        if not schedule_config or not schedule_config.is_enabled:
            # Удаляем задачу если она есть
            beat_schedule = current_app.conf.beat_schedule
            if 'scheduled_smb_indexing' in beat_schedule:
                del beat_schedule['scheduled_smb_indexing']
                current_app.conf.beat_schedule = beat_schedule
            logger.info("Расписание индексации SMB отключено")
            return
        
        # Создаем расписание в зависимости от типа
        schedule = None
        
        if schedule_config.schedule_type == 'hourly':
            schedule = crontab(minute=schedule_config.custom_minute)
        elif schedule_config.schedule_type == 'daily':
            schedule = crontab(
                hour=schedule_config.custom_hour,
                minute=schedule_config.custom_minute
            )
        elif schedule_config.schedule_type == 'weekly':
            schedule = crontab(
                hour=schedule_config.custom_hour,
                minute=schedule_config.custom_minute,
                day_of_week=schedule_config.custom_day_of_week
            )
        elif schedule_config.schedule_type == 'monthly':
            schedule = crontab(
                hour=schedule_config.custom_hour,
                minute=schedule_config.custom_minute,
                day_of_month=schedule_config.custom_day_of_month
            )
        elif schedule_config.schedule_type == 'custom':
            schedule = crontab(
                hour=schedule_config.custom_hour,
                minute=schedule_config.custom_minute,
                day_of_week=schedule_config.custom_day_of_week if schedule_config.custom_day_of_week >= 0 else None,
                day_of_month=schedule_config.custom_day_of_month if schedule_config.custom_day_of_month > 0 else None
            )
        
        if schedule:
            # Обновляем задачу в Celery Beat
            current_app.conf.beat_schedule['scheduled_smb_indexing'] = {
                'task': 'statement.tasks.refresh_smb_index',
                'schedule': schedule,
                'options': {
                    'expires': 3600,  # Задача устаревает через час
                }
            }
            logger.info(f"Расписание индексации SMB обновлено: {schedule_config}")
            
            # Обновляем next_run (приблизительно)
            # Не обновляем здесь, чтобы избежать проблем с транзакциями
            # Это будет сделано отдельно
            
    except Exception as e:
        logger.error(f"Ошибка при обновлении расписания: {e}")


# Функция для инициализации расписания при старте
def init_smb_scheduler():
    """Инициализирует планировщик SMB при запуске"""
    try:
        if not SMBIndexSchedule.objects.exists():
            # Создаем настройки по умолчанию
            SMBIndexSchedule.objects.create(
                is_enabled=True,
                schedule_type='daily',
                custom_hour=2,
                custom_minute=0
            )
            logger.info("Созданы настройки индексации SMB по умолчанию")
        
        update_smb_indexing_schedule()
    except Exception as e:
        logger.error(f"Ошибка при инициализации планировщика: {e}")