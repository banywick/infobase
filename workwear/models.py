from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Employee(models.Model):
    """Модель сотрудника"""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='employee_profile'
    )
    employee_id = models.CharField(max_length=20, unique=True, verbose_name="Табельный номер")
    department = models.CharField(max_length=100, verbose_name="Отдел")
    position = models.CharField(max_length=100, verbose_name="Должность")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email")
    photo = models.URLField(blank=True, null=True, verbose_name="Фото (URL из LDAP)")
    ldap_dn = models.CharField(max_length=255, blank=True, verbose_name="LDAP DN")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        ordering = ['user__last_name', 'user__first_name']

    def __str__(self):
        return f"{self.user.last_name} {self.user.first_name}"

    def get_full_name(self):
        return f"{self.user.last_name} {self.user.first_name} {self.user.patronymic}" if hasattr(self.user, 'patronymic') else f"{self.user.last_name} {self.user.first_name}"

    def get_expiring_items(self):
        """Получить спецодежду с истекающим сроком"""
        today = timezone.now().date()
        threshold = today + timedelta(days=30)  # Уведомление за 30 дней
        return self.workwear_items.filter(
            expiration_date__gte=today,
            expiration_date__lte=threshold,
            is_active=True
        )

    def get_expired_items(self):
        """Получить просроченную спецодежду"""
        today = timezone.now().date()
        return self.workwear_items.filter(
            expiration_date__lt=today,
            is_active=True
        )

class WorkwearCategory(models.Model):
    """Категория спецодежды"""
    name = models.CharField(max_length=100, verbose_name="Название категории")
    description = models.TextField(blank=True, verbose_name="Описание")
    standard_lifespan = models.PositiveIntegerField(
        default=365, 
        verbose_name="Стандартный срок эксплуатации (дней)"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Категория спецодежды"
        verbose_name_plural = "Категории спецодежды"
        ordering = ['name']

    def __str__(self):
        return self.name

class WorkwearItem(models.Model):
    """Предмет спецодежды"""
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE,
        related_name='workwear_items',
        verbose_name="Сотрудник"
    )
    category = models.ForeignKey(
        WorkwearCategory,
        on_delete=models.CASCADE,
        related_name='workwear_items',
        verbose_name="Категория"
    )
    name = models.CharField(max_length=200, verbose_name="Наименование")
    serial_number = models.CharField(max_length=50, blank=True, verbose_name="Серийный номер")
    size = models.CharField(max_length=20, blank=True, verbose_name="Размер")
    color = models.CharField(max_length=30, blank=True, verbose_name="Цвет")
    issue_date = models.DateField(verbose_name="Дата выдачи")
    expiration_date = models.DateField(verbose_name="Дата окончания срока эксплуатации")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    notes = models.TextField(blank=True, verbose_name="Примечания")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Предмет спецодежды"
        verbose_name_plural = "Предметы спецодежды"
        ordering = ['employee', 'category', 'name']

    def __str__(self):
        return f"{self.name} - {self.employee.get_full_name()}"

    def get_status(self):
        """Получить статус предмета"""
        today = timezone.now().date()
        if self.expiration_date < today:
            return 'expired'
        elif self.expiration_date <= today + timedelta(days=30):
            return 'expiring_soon'
        else:
            return 'active'

    def is_expired(self):
        return self.expiration_date < timezone.now().date()

    def is_expiring_soon(self):
        today = timezone.now().date()
        return self.expiration_date <= today + timedelta(days=30) and not self.is_expired()

class WorkwearHistory(models.Model):
    """История изменений спецодежды"""
    ACTION_CHOICES = [
        ('issued', 'Выдана'),
        ('returned', 'Возвращена'),
        ('written_off', 'Списана'),
        ('replaced', 'Заменена'),
        ('updated', 'Обновлена'),
    ]
    
    workwear_item = models.ForeignKey(
        WorkwearItem,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name="Предмет спецодежды"
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="Действие")
    previous_employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='workwear_history_previous',
        verbose_name="Предыдущий сотрудник"
    )
    new_employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='workwear_history_new',
        verbose_name="Новый сотрудник"
    )
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='workwear_history_created',
        verbose_name="Кем создано"
    )

    class Meta:
        verbose_name = "История спецодежды"
        verbose_name_plural = "История спецодежды"
        ordering = ['-created_at']