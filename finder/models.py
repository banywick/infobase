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



# class StandartsName(models.Model):
#     STANDARD_CHOICES = [
#         ('DIN', 'DIN'),
#         ('GOST', 'ГОСТ'),
#         ('ISO', 'ISO'),
#     ]

#     name = models.CharField(
#         max_length=255,
#         choices=STANDARD_CHOICES,
#         verbose_name='Стандарт'
#     )
#     title = models.CharField(
#         null=True, blank=True,
#         max_length=255,
#         verbose_name='Название'
#     )
    

#     def __str__(self):
#         return self.name

#     class Meta:
#         verbose_name = 'Стандарт'
#         verbose_name_plural = 'Стандарты'


# class StandartsValue(models.Model):
#     standarts_name = models.ForeignKey(StandartsName, on_delete=models.CASCADE, related_name='values_st', verbose_name='Стандарт')
#     value = models.CharField(null=True, blank=True, max_length=255, verbose_name='Значение')

#     def __str__(self):
#         return self.value

#     class Meta:
#         verbose_name = 'Значение стандарта'
#         verbose_name_plural = 'Значение стандартов' 


class CategoryProduct(models.Model):
    category_product =  models.CharField(max_length=255, verbose_name='Категория')

    def __str__(self):
        return self.category_product

    class Meta:
        verbose_name = 'Категория товара'
        verbose_name_plural = 'Категории товаров' 

class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары' 

class Analog(models.Model):
    product = models.ForeignKey(Product, related_name='analogs', on_delete=models.CASCADE, verbose_name='Название или стандарт')
    category = models.ForeignKey(CategoryProduct, related_name='category', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Категория')  # Стандарт, например, "GOST", "DIN", "ISO"
    analog_name = models.CharField(max_length=255, verbose_name='Аналог названия')  # Код аналога

    def __str__(self):
        return f"{self.product.name} = {self.analog_name} = {self.category} "
    
    class Meta:
        verbose_name = 'Аналоги'
        verbose_name_plural = 'Аналоги' 