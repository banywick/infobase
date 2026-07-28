from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Employee

@receiver(post_save, sender=User)
def create_employee_profile(sender, instance, created, **kwargs):
    """Создает профиль сотрудника при создании пользователя"""
    if created:
        Employee.objects.create(
            user=instance,
            employee_id=instance.username,  # Временное решение, можно заменить на данные из LDAP
            email=instance.email,
            department='Не указан',
            position='Не указана'
        )

@receiver(post_save, sender=User)
def save_employee_profile(sender, instance, **kwargs):
    """Сохраняет профиль сотрудника при сохранении пользователя"""
    try:
        instance.employee_profile.save()
    except Employee.DoesNotExist:
        Employee.objects.create(
            user=instance,
            employee_id=instance.username,
            email=instance.email,
            department='Не указан',
            position='Не указана'
        )