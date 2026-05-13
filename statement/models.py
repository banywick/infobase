# statement/models.py

from django.db import models
from django.utils import timezone


class SMBPathConfig(models.Model):
    """
    Модель для хранения настроек путей SMB
    """
    CONFIG_TYPE_CHOICES = [
        ('search', 'Поиск ВК (незаполненные ведомости)'),
        ('accounting_source', 'Accounting Data Source (готовые ведомости)'),
    ]
    
    name = models.CharField(
        max_length=100, 
        unique=True,
        verbose_name="Название настройки"
    )
    config_type = models.CharField(
        max_length=20,
        choices=CONFIG_TYPE_CHOICES,
        default='search',
        verbose_name="Тип конфигурации"
    )
    search_path = models.CharField(
        max_length=500,
        verbose_name="Путь для поиска файлов",
        help_text="Например: \\\\10.29.107.16\\папка"
    )
    result_path = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Путь для сохранения результатов (только для поиска ВК)",
        help_text="Для конфигураций типа 'Поиск ВК'"
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
        ordering = ['config_type', '-is_active', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_config_type_display()})"


class SMBFileIndex(models.Model):
    """
    Модель для хранения индекса файлов из SMB
    """
    FILE_TYPE_CHOICES = [
        ('xlsx', 'Excel XLSX'),
        ('xls', 'Excel XLS'),
        ('xlsm', 'Excel XLSM'),
    ]
    
    PROCESSING_STATUS_CHOICES = [
        ('pending', 'Ожидает обработки'),
        ('processing', 'В обработке'),
        ('processed', 'Обработан'),
        ('error', 'Ошибка'),
        ('skipped', 'Пропущен'),
    ]
    
    config = models.ForeignKey(
        SMBPathConfig, 
        on_delete=models.CASCADE,
        related_name='indexed_files',
        verbose_name="Конфигурация SMB"
    )
    
    filename = models.CharField(max_length=255, verbose_name="Имя файла")
    file_extension = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES, verbose_name="Тип файла")
    file_path = models.CharField(max_length=1000, verbose_name="Полный путь к файлу")
    relative_path = models.CharField(max_length=1000, verbose_name="Относительный путь", blank=True)
    file_size = models.BigIntegerField(null=True, blank=True, verbose_name="Размер файла (байт)")
    modified_time = models.DateTimeField(null=True, blank=True, verbose_name="Время изменения")
    
    is_available = models.BooleanField(default=True, verbose_name="Доступен")
    last_checked = models.DateTimeField(auto_now=True, verbose_name="Последняя проверка")
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Новые поля для отслеживания обработки
    processing_status = models.CharField(
        max_length=20,
        choices=PROCESSING_STATUS_CHOICES,
        default='pending',
        verbose_name="Статус обработки"
    )
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name="Время обработки")
    processing_error = models.TextField(blank=True, verbose_name="Ошибка обработки")
    
    class Meta:
        verbose_name = "Индекс SMB файла"
        verbose_name_plural = "Индексы SMB файлов"
        unique_together = ['config', 'file_path']
        indexes = [
            models.Index(fields=['config', 'is_available', 'processing_status']),
            models.Index(fields=['config', 'file_extension']),
            models.Index(fields=['processing_status', 'is_available']),
        ]
    
    def __str__(self):
        return f"{self.filename} ({self.get_processing_status_display()}) - {self.config.name}"
    
    def mark_as_processed(self):
        """Отмечает файл как обработанный"""
        self.processing_status = 'processed'
        self.processed_at = timezone.now()
        self.save(update_fields=['processing_status', 'processed_at'])
    
    def mark_as_error(self, error_message):
        """Отмечает файл с ошибкой"""
        self.processing_status = 'error'
        self.processing_error = error_message
        self.save(update_fields=['processing_status', 'processing_error'])
    
    def mark_as_processing(self):
        """Отмечает файл как обрабатываемый"""
        self.processing_status = 'processing'
        self.save(update_fields=['processing_status'])


class ProcessedFileLog(models.Model):
    """
    Лог обработанных файлов для отслеживания истории
    """
    file_index = models.ForeignKey(
        SMBFileIndex,
        on_delete=models.CASCADE,
        related_name='processing_logs',
        verbose_name="Файл"
    )
    processed_at = models.DateTimeField(auto_now_add=True, verbose_name="Время обработки")
    rows_processed = models.IntegerField(default=0, verbose_name="Обработано строк")
    status = models.CharField(
        max_length=20,
        choices=SMBFileIndex.PROCESSING_STATUS_CHOICES,
        default='processed',
        verbose_name="Статус"
    )
    error_message = models.TextField(blank=True, verbose_name="Ошибка")
    
    class Meta:
        verbose_name = "Лог обработанных файлов"
        verbose_name_plural = "Логи обработанных файлов"
        ordering = ['-processed_at']
    
    def __str__(self):
        return f"{self.file_index.filename} - {self.processed_at}"