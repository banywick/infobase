# common/models.py
from django.db import models

class UniqueIP(models.Model):
    """База с унакальными ip c запросов к сервису"""
    ip_address = models.GenericIPAddressField(unique=True)
    first_request_time = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, blank=True, null=True)


class RequestCounter(models.Model):
    """Счетчик всех запросов к сервису"""
    count = models.IntegerField(default=0)

