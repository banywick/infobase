# statement/apps.py
from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class StatementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'statement'
    verbose_name = 'Ведомости и SMB'

    def ready(self):
        """
        Инициализация приложения
        """
        try:
            # Импортируем сигналы
            import statement.signals
            logger.info("✅ Сигналы statement загружены")
            
            # Импортируем планировщик (только если не в миграциях)
            import os
            if not os.environ.get('RUN_MAIN') == 'true' and not os.environ.get('MIGRATING'):
                from .scheduler import init_smb_scheduler
                init_smb_scheduler()
                logger.info("✅ Планировщик SMB инициализирован")
                
        except Exception as e:
            logger.warning(f"⚠️ Ошибка при инициализации statement: {e}")