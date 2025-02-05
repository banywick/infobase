from django.apps import AppConfig


class SahrConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sahr'

    def ready(self):
        import sahr.signals  # Импортируйте файл с сигналами



