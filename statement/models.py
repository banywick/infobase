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



# models.py - добавить новую модель

class SMBFileIndex(models.Model):
    """
    Модель для хранения индекса файлов из SMB
    """
    FILE_TYPE_CHOICES = [
        ('xlsx', 'Excel XLSX'),
        ('xls', 'Excel XLS'),
        ('xlsm', 'Excel XLSM'),
    ]
    
    # Связь с конфигурацией
    config = models.ForeignKey(
        SMBPathConfig, 
        on_delete=models.CASCADE,
        related_name='indexed_files',
        verbose_name="Конфигурация SMB"
    )
    
    # Информация о файле
    filename = models.CharField(max_length=255, verbose_name="Имя файла")
    file_extension = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES, verbose_name="Тип файла")
    file_path = models.CharField(max_length=1000, verbose_name="Полный путь к файлу")
    relative_path = models.CharField(max_length=1000, verbose_name="Относительный путь", blank=True)
    file_size = models.BigIntegerField(null=True, blank=True, verbose_name="Размер файла (байт)")
    modified_time = models.DateTimeField(null=True, blank=True, verbose_name="Время изменения")
    
    # Мета информация
    is_available = models.BooleanField(default=True, verbose_name="Доступен")
    last_checked = models.DateTimeField(auto_now=True, verbose_name="Последняя проверка")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Индекс SMB файла"
        verbose_name_plural = "Индексы SMB файлов"
        unique_together = ['config', 'file_path']  # Однозначная идентификация
        indexes = [
            models.Index(fields=['config', 'is_available', 'filename']),
            models.Index(fields=['config', 'file_extension']),
        ]
    
    def __str__(self):
        return f"{self.filename} ({self.get_file_extension_display()}) - {self.config.name}"




