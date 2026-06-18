# cars/models.py
from django.db import models


class Location(models.Model):
    """Модель для управления местами хранения"""
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Название места хранения"
    )
    code = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Код места хранения"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активно"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
    
    class Meta:
        verbose_name = "Место хранения"
        verbose_name_plural = "Места хранения"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class InventoryItem(models.Model):
    """Основная таблица учета"""
    
    number = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name="№ТН, ТТН"
    )
    
    arrival_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name="Дата поступления"
    )
    
    article = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        verbose_name="Код (Артикул)"
    )
    
    name = models.CharField(
        max_length=255, 
        blank=True,
        verbose_name="Наименование"
    )
    
    # Изменяем поле на ForeignKey к модели Location
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Место хранения"
    )
    
    quantity = models.IntegerField(
        null=True, 
        blank=True,
        verbose_name="Кол-во"
    )
    
    comment = models.TextField(
        blank=True,
        verbose_name="Комментарии"
    )
    
    # Поле для иерархии (родительская позиция)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="Родительская позиция"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
    
    class Meta:
        verbose_name = "Техника"
        verbose_name_plural = "Техника"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.number} - {self.name or self.article}"