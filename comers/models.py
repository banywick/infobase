from django.db import models

class Comment(models.Model):
    text = models.CharField(max_length=255, verbose_name='Текст')

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Комментарий склада'
        verbose_name_plural = 'Комментарии склада'

class Leading(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ведущий'
        verbose_name_plural = 'Ведущие'

class Supler(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'

class Status(models.Model):
    name = models.CharField(max_length=100, default='Запрос', verbose_name='Статус')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'

class Specialist(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Специалист'
        verbose_name_plural = 'Специалисты'


class Invoice(models.Model):
    invoice_number = models.CharField(max_length=20, verbose_name='Номер счета')
    date = models.DateField(verbose_name='Дата')
    supplier = models.ForeignKey(Supler, on_delete=models.CASCADE, verbose_name='Поставщик')
    article = models.CharField(max_length=100, verbose_name='Артикул')
    project = models.CharField(max_length=100, blank=True, null=True, verbose_name='Проект')
    name = models.CharField(max_length=100, verbose_name='Название')
    unit = models.CharField(max_length=50, default='шт', verbose_name='Единица измерения')
    quantity = models.FloatField(verbose_name='Количество')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, verbose_name='Комментарий')
    description_problem = models.TextField(blank=True, null=True, verbose_name='Описание проблемы')
    specialist = models.ForeignKey(Specialist, on_delete=models.CASCADE, verbose_name='Специалист')
    leading = models.ForeignKey(Leading, on_delete=models.CASCADE, verbose_name='Руководитель')
    status = models.ForeignKey(Status, on_delete=models.CASCADE, default=5, verbose_name='Статус')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')


    def __str__(self):
        return self.invoice_number

    class Meta:
        verbose_name = 'Позиции в обработке'
        verbose_name_plural = 'Позиции в обработке'