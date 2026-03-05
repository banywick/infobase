from django.db import models

class Review(models.Model):
    user = models.CharField(null=True, blank=True, verbose_name='Пользователь')
    text = models.TextField(verbose_name='Отзыв')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')

    def __str__(self):
        return f'{self.user} {self.created_at} {self.text}'
    
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы' 





class NewsItem(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    link = models.URLField(blank=True, null=True, verbose_name="Ссылка")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"


