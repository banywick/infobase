from django.db import models

class Data_Table(models.Model):
    index_remains = models.IntegerField(blank=True, null=True, verbose_name='')
    article = models.CharField(max_length=60, verbose_name='Артикул')
    party = models.CharField(max_length=20, verbose_name='Партия')
    title = models.TextField(verbose_name='Название')
    base_unit = models.CharField(max_length=10, blank=True, null=True,
                                verbose_name='Единица')
    comment = models.TextField(blank=True, null=True, verbose_name='Комментарий')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    address = models.CharField(max_length=100, verbose_name='Адрес')

    def __str__(self):
        return self.article

    def save(self, *args, **kwargs):
        # Обрезаем пробелы в начале и конце строки поля my_field
        self.my_field = self.article.strip()
        super(Data_Table, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'С.А.ХР'


class History(models.Model):
    data_table = models.ForeignKey(Data_Table, on_delete=models.CASCADE, verbose_name='')
    article = models.TextField(null=True, verbose_name='Артикул')
    party = models.CharField(max_length=9, null=True, verbose_name='Партия')
    title = models.TextField(null=True, verbose_name='Название')
    comment = models.TextField(null=True, verbose_name='Комментарий')
    date = models.DateTimeField(null=True, verbose_name='Дата именения')
    address = models.CharField(max_length=100, null=True, verbose_name='Адрес')

    def __str__(self):
        return self.article
    
    class Meta:
        verbose_name_plural = 'История изменений'


class Deleted(models.Model):
    article = models.TextField(null=True, verbose_name='Артикул')
    party = models.CharField(max_length=9, null=True, verbose_name='Партия')
    title = models.TextField(null=True, verbose_name='Название')
    comment = models.TextField(null=True, verbose_name='Комментарий')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата удаления')
    address = models.CharField(max_length=100, null=True, verbose_name='Адрес')

    def __str__(self):
        return self.article
    
    class Meta:
        verbose_name_plural = 'Архив'
