from django.db import models

class Data_Table(models.Model):
    index_remains = models.IntegerField(blank=True, null=True, default=1)
    article = models.CharField(max_length=60,blank=True, null=True)
    party = models.CharField(max_length=20, blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    base_unit = models.CharField(max_length=10, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.article

    def save(self, *args, **kwargs):
        # Обрезаем пробелы в начале и конце строки поля my_field
        self.my_field = self.article.strip()
        super(Data_Table, self).save(*args, **kwargs)


class History(models.Model):
    data_table = models.ForeignKey(Data_Table, on_delete=models.CASCADE)
    article = models.TextField(null=True)
    party = models.CharField(max_length=9, null=True)
    title = models.TextField(null=True)
    comment = models.TextField(null=True)
    date = models.DateTimeField(null=True)
    address = models.CharField(max_length=100, null=True)


class Deleted(models.Model):
    article = models.TextField(null=True)
    party = models.CharField(max_length=9, null=True)
    title = models.TextField(null=True)
    comment = models.TextField(null=True)
    date = models.DateTimeField(auto_now_add=True)
    address = models.CharField(max_length=100, null=True)
