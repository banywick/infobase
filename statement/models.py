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



# statement/models.py - добавить новую модель

class SMBIndexSchedule(models.Model):
    """
    Модель для настройки расписания индексации
    """
    # Периодичность индексации
    SCHEDULE_CHOICES = [
        ('disabled', 'Отключено'),
        ('hourly', 'Каждый час'),
        ('daily', 'Ежедневно'),
        ('weekly', 'Еженедельно'),
        ('monthly', 'Ежемесячно'),
        ('custom', 'Своё расписание'),
    ]
    
    is_enabled = models.BooleanField(
        default=True,
        verbose_name="Включить автоматическую индексацию"
    )
    
    schedule_type = models.CharField(
        max_length=20,
        choices=SCHEDULE_CHOICES,
        default='daily',
        verbose_name="Периодичность"
    )
    
    # Для кастомного расписания
    custom_hour = models.IntegerField(
        default=2,
        choices=[(h, f"{h:02d}:00") for h in range(24)],
        verbose_name="Час (0-23)",
        help_text="Для ежедневного или кастомного расписания"
    )
    
    custom_minute = models.IntegerField(
        default=0,
        choices=[(m, f"{m:02d}") for m in range(0, 60, 5)],
        verbose_name="Минута (0-55 с шагом 5)",
        help_text="Для точной настройки времени"
    )
    
    custom_day_of_week = models.IntegerField(
        default=1,
        choices=[(i, day) for i, day in enumerate(['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'])],
        verbose_name="День недели",
        help_text="Для еженедельного расписания"
    )
    
    custom_day_of_month = models.IntegerField(
        default=1,
        choices=[(i, str(i)) for i in range(1, 29)] + [(28, '28'), (29, '29'), (30, '30'), (31, '31')],
        verbose_name="День месяца",
        help_text="Для ежемесячного расписания (1-31)"
    )
    
    last_run = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Последний запуск"
    )
    next_run = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Следующий запуск"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Расписание индексации SMB"
        verbose_name_plural = "Расписание индексации SMB"
    
    def __str__(self):
        if not self.is_enabled:
            return "Индексация SMB: Отключена"
        
        if self.schedule_type == 'disabled':
            return "Индексация SMB: Отключена"
        elif self.schedule_type == 'hourly':
            return "Индексация SMB: Каждый час"
        elif self.schedule_type == 'daily':
            return f"Индексация SMB: Ежедневно в {self.custom_hour:02d}:{self.custom_minute:02d}"
        elif self.schedule_type == 'weekly':
            days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
            return f"Индексация SMB: Еженедельно по {days[self.custom_day_of_week]} в {self.custom_hour:02d}:{self.custom_minute:02d}"
        elif self.schedule_type == 'monthly':
            return f"Индексация SMB: Ежемесячно {self.custom_day_of_month}-го числа в {self.custom_hour:02d}:{self.custom_minute:02d}"
        else:
            return f"Индексация SMB: Кастомное расписание"