# common/middleware.py
from .models import UniqueIP
from .models import RequestCounter

class UniqueIPMiddleware:
    """Получение уникальных ip адресов запрашивающих сервис"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Получаем IP-адрес пользователя
        ip_address = self.get_client_ip(request)

        # Сохраняем IP-адрес, если он уникален
        if ip_address:
            UniqueIP.objects.get_or_create(ip_address=ip_address)

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip



class RequestCounterMiddleware:
    """Счетчик запросов"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Увеличиваем счетчик запросов
        counter, created = RequestCounter.objects.get_or_create(id=1)
        counter.count += 1
        counter.save()

        response = self.get_response(request)
        return response