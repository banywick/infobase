from django.db import models

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
    
    location = models.CharField(
        max_length=255,
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
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    
    class Meta:
        db_table = 'inventory_items'
        verbose_name = "Инвентарная запись"
        verbose_name_plural = "Инвентарные записи"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.number} - {self.name or self.article}"