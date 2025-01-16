import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Remains
from .serializers import RemainsSerializer
from django.db.models import Q
from django.views.generic import TemplateView
from django.core.cache import cache

logger = logging.getLogger(__name__)

class HomeView(TemplateView):
    template_name = 'index.html'


class ProductSearchView(APIView):
    def post(self, request, *args, **kwargs):
        query = request.data.get('query', '')
        search_by_code = request.data.get('search_by_code', False)
        search_by_comment = request.data.get('search_by_comment', False)
        search_by_analogs = request.data.get('search_by_analogs', False)

        # Ключ для кэша
        cache_key = 'remains_all_queryset'

        # Попытка получить данные из кэша
        queryset = cache.get(cache_key)

        if not queryset:
            # Если данных нет в кэше, выполняем запрос к базе данных
            queryset = Remains.objects.all()
            # Кэшируем результат на 24 часа
            cache.set(cache_key, queryset, 60 * 60 * 24)
            logger.info("Добавлен в КЭШ!!!!!")

        # Добавляем условия в зависимости от выбранных чекбоксов
        if search_by_code:
            queryset = queryset.filter(Q(code__icontains=query))
        elif search_by_comment:
            queryset = queryset.filter(Q(comment__icontains=query))
        # elif search_by_analogs:
        #     queryset = queryset.filter(Q(analogs__icontains=query))
        else:
            queryset = queryset.filter(Q(title__icontains=query))

        serializer = RemainsSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)  

