from django.db import models
from django.contrib.auth.models import User

class Remains(models.Model):
    comment = models.CharField(max_length=50, null=True, verbose_name='Комментарий')
    code = models.CharField(max_length=50, null=True, verbose_name='Код')
    article = models.TextField(null=True, verbose_name='Артикул')
    party = models.CharField(max_length=9, null=True, verbose_name='Партия')
    title = models.TextField(null=True, verbose_name='Наименование')
    base_unit = models.CharField(max_length=10, null=True, verbose_name='Единица')
    project = models.CharField(max_length=30, null=True, verbose_name='Проект')
    quantity = models.FloatField(blank=True, null=True, verbose_name='Количество')
    price = models.IntegerField(null=True)


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


class Standard(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255)

    def __str__(self):
        return self.code

class Item(models.Model):
    TYPE_CHOICES = [
        ('bolt', 'Болт'),
        ('nut', 'Гайка'),
        ('washer', 'Шайба'),
        ('ring', 'Кольцо'),
        ('screw', 'Винт'),
        ('pin', 'Шпилька'),
        ('split_pin', 'Шплинт'),
        ('dowel', 'Штифт'),
        ('key', 'Шпонка'),
        ('rivet', 'Заклепка'),
        ('threaded_insert', 'Вставка (втулка) резьбовая (сменная)'),
        ('clamp', 'Хомут'),
        ('half_ring', 'Полукольцо'),
    ]
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    standards = models.ManyToManyField(Standard, related_name='items')

    def __str__(self):
        return f"{self.get_type_display()} {self.id}"