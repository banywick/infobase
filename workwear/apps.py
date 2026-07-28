from django.apps import AppConfig


class WorkwearConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'workwear'

    def ready(self):
        import workwear.signals
