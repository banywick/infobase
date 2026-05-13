# statement/apps.py
from django.apps import AppConfig
import logging
import sys

logger = logging.getLogger(__name__)


class StatementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'statement'
    verbose_name = 'Ведомости и SMB'

    def ready(self):
        """Инициализация приложения"""
        if 'migrate' in sys.argv or 'makemigrations' in sys.argv:
            return
        
        try:
            import statement.signals
            logger.info("✅ Сигналы statement загружены")
        except Exception as e:
            logger.error(f"❌ Ошибка при загрузке сигналов: {e}")