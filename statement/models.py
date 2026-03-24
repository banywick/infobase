# models.py

from django.db import models

class SMBPathConfig(models.Model):
    """
    Модель для хранения настроек путей SMB
    """
    name = models.CharField(
        max_length=100, 
        unique=True,
        verbose_name="Название настройки"
    )
    search_path = models.CharField(
        max_length=500,
        verbose_name="Путь для поиска файлов ВК",
        help_text="Например: \\\\10.29.107.16\\белоус а.н\\тест скрипта"
    )
    result_path = models.CharField(
        max_length=500,
        verbose_name="Путь для сохранения результатов",
        help_text="Например: \\\\10.29.107.16\\белоус а.н\\результат"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активна"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Настройка SMB пути"
        verbose_name_plural = "Настройки SMB путей"
        ordering = ['-is_active', 'name']
    
    def __str__(self):
        return f"{self.name} ({'активна' if self.is_active else 'неактивна'})"