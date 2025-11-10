from django.db import models

class UniqueIP(models.Model):
    """База с уникальными IP с запросов к сервису"""
    ip_address = models.GenericIPAddressField(unique=True)
    first_request_time = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Уникальный IP"
        verbose_name_plural = "Уникальные IP"

class RequestCounter(models.Model):
    """Счетчик всех запросов к сервису"""
    count = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Счетчик запросов"
        verbose_name_plural = "Счетчики запросов"
