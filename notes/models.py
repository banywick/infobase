from django.db import models
from django.contrib.auth.models import User

class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,  verbose_name='Пользователь')
    text = models.TextField( verbose_name='Заметка')

    def __str__(self):
        return f'Note by {self.user.username} {self.text}'
    
    class Meta:
        verbose_name = 'Заметка'
        verbose_name_plural = 'Заметки' 
