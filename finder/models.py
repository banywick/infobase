from django.db import models
from django.contrib.auth.models import Group

class Remains(models.Model):
    notes_part = models.CharField(max_length=50, null=True, verbose_name='Примечания')
    comment = models.CharField(max_length=50, null=True, verbose_name='Комментарий')
    code = models.CharField(max_length=50, null=True, verbose_name='Код')
    article = models.TextField(null=True, verbose_name='Артикул')
    party = models.CharField(max_length=9, null=True, verbose_name='Партия')
    title = models.TextField(null=True, verbose_name='Наименование')
    base_unit = models.CharField(max_length=10, null=True, verbose_name='Единица')
    project = models.CharField(max_length=30, null=True, verbose_name='Проект')
    quantity = models.FloatField(blank=True, null=True, verbose_name='Количество')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Используйте DecimalField


    def __str__(self):
        return f"{self.article}"
    

    def save(self, *args, **kwargs):
        # Обрезаем пробелы в начале и конце строки поля my_field
        self.my_field = self.article.strip()
        super(Remains, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Остаток'
        verbose_name_plural = 'Остатки'  



class Review(models.Model):
    user = models.CharField(null=True, blank=True, verbose_name='Пользователь')
    text = models.TextField(verbose_name='Отзыв')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')

    def __str__(self):
        return f'{self.user} {self.created_at} {self.text}'
    
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'  





class ProjectStatus(models.Model):
    # Choice field для project_name
    project_name = models.CharField(max_length=255, verbose_name="Название проекта")

    # Choice field для color
    COLOR_CHOICES = [
        ('red', 'Red'),
        ('green', 'Green'),
        ('gray', 'Gray'),  # Значение по умолчанию
    ]
    color = models.CharField(
        max_length=50,
        choices=COLOR_CHOICES,
        default='gray',  # Значение по умолчанию
        verbose_name="Цвет точки (CSS-класс или hex-код)"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Динамически заполняем choices для project_name
        self._meta.get_field('project_name').choices = self.get_project_choices()

    @staticmethod
    def get_project_choices():
        # Получаем уникальные значения project_name из другой таблицы
        from .models import Remains  # Импортируем модель Remains
        projects = Remains.objects.values_list('project', flat=True).distinct()
        return [(project, project) for project in projects]

    def __str__(self):
        return f"{self.project_name} - {self.color}"

    class Meta:
        verbose_name = "Статус проекта"
        verbose_name_plural = "Статусы проектов"


    
class LinkAccess(models.Model):
    """
    Для возможности управлять какой группе
    какие ссылки из меню отображать 
    
    """
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name='')
    LINK_NAMES = [
        ('поиск', 'Поиск'),
        ('заметки', 'Заметки'),
        ('сахр', 'Сахр'),  
        ('архив', 'Архив'), 
        ('недопоставки', 'Недопоставки'),  
        ('инвентаризация', 'Инвентаризация'),  
        ('таблица аналогов', 'Таблица аналогов'), 
        ('бтк', 'БТК'),
        ('отзывы и предложения', 'Отзывы и предложения'), 
        ('обновить базу', 'Обновить базу'),  
    ]
    link_name = models.CharField(
        max_length=20, choices=LINK_NAMES, verbose_name='Строка меню')

    def __str__(self):
        return f"{self.group.name} - {self.link_name}"
    
    class Meta:
        verbose_name = "Доступ по ссылкам"
        verbose_name_plural = "Доступы по ссылкам"




class Standard(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Коллекция')  # Например "standart38"

    def __str__(self) -> str:
        return f"{self.name}"

class StandardValue(models.Model):
    standard = models.ForeignKey(Standard, on_delete=models.CASCADE, related_name='values', verbose_name='Коллекция')
    value = models.CharField(max_length=50)  # Храним как строку для универсальности

    def __str__(self):
        return f"{self.value}"

    class Meta:
        unique_together = ('standard', 'value')  # Запрещаем дубликаты
        ordering = ['value']  # Сортировка по значению
        verbose_name = "Аналоги"
        verbose_name_plural = "Аналоги"