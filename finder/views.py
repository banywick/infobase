import logging
from turtle import st
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils.add_session_data import SessionManager
from .utils.metiz import process_metiz_query
from .models import  Metiz, Remains, Standard
from .serializers import RemainsSerializer
from django.db.models import Q
from django.views.generic import TemplateView
from django.core.cache import cache
from django.db.models import Sum
from .serializers import ProjectListSerializer

logger = logging.getLogger(__name__)


def get_cached_remains_queryset():
    """Создание КЭША из queryset Remains"""
    cache_key = 'remains_all_queryset'
    queryset = cache.get(cache_key)

    if not queryset:
        queryset = Remains.objects.all()
        cache.set(cache_key, queryset, 60 * 60 * 24)
        logger.info("Добавлен в КЭШ!!!!!")

    return queryset

class HomeView(TemplateView):
    """Главня станица"""
    logger.info("HELLLOO")
    template_name = 'index.html'


class ProductSearchView(APIView):
    """Поисковые фильтры, условия поиска"""
    def post(self, request, *args, **kwargs):
        query = request.data.get('query', '')
        search_by_code = request.data.get('search_by_code', False)
        search_by_comment = request.data.get('search_by_comment', False)
        search_by_analogs = request.data.get('search_by_analogs', False)

        # Попытка получить данные из кэша
        # queryset = get_cached_remains_queryset()
        queryset = queryset = Remains.objects.all()

        # standarts = ItemStandarts.objects.filter(Q(type='bolt') & Q(type_standarts='GOST'))
        # for i in standarts:
        #     print(i.type_standarts, i.number)

        # Разделение ввода на слова
        values = query.split()

        # Создание Q-объектов для каждого слова
        q_objects = Q()
        for value in values:
            current_q = Q()
            if search_by_code:
                q_objects &= Q(code__icontains=value)
            if search_by_comment:
                q_objects &= Q(comment__icontains=value) 
            if search_by_analogs:
                q_objects &= Q(title__icontains=value)

                standards = Standard.objects.prefetch_related('metizes').filter(id=1)
                for i in standards:
                    print(i.number)
                
               
            # По умолчанию ищем по title или comment
            current_q &= (Q(title__icontains=value) | Q(comment__icontains=value) | Q(article__icontains=value))
            q_objects &= current_q 

            # Дополнительная логика для метизов
            metiz_all, replace_a = process_metiz_query(value)
            current_q &= metiz_all
            current_q &= replace_a

            q_objects &= current_q

        # Применение фильтров
        queryset = queryset.filter(q_objects)

        serializer = RemainsSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)  
    


class RemainsDetailView(APIView):
    """Детализация позиции по артикулу
    общая сумма, все партии и проеты"""
    def get(self, request, article):

        # Получаем все позиции с указанным артикулом
        positions = Remains.objects.filter(article=article)

        # Суммируем количество по одинаковым артикулам
        total_quantity = positions.aggregate(total_quantity=Sum('quantity'))['total_quantity']

        if total_quantity is None:
            return Response({"error": "Position not found"}, status=status.HTTP_404_NOT_FOUND)

        # Получаем все проекты и партии, связанные с этим артикулом
        projects = positions.values_list('project', flat=True).distinct()
        partys = positions.values_list('party', flat=True).distinct()

        # Создаем словарь с данными для ответа
        data = {
            'article': article,
            'total_quantity': total_quantity,
            'projects': list(projects),
            'party': list(partys)
        }

        return Response(data, status=status.HTTP_200_OK)    

class ProjectListView(APIView):
    """Весь список уникальных проектов"""
    def get(self, request):

        # Получаем все уникальные проекты
        unique_projects = Remains.objects.values('project').distinct()

        # Сериализуем данные
        serializer = ProjectListSerializer(unique_projects, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    

class AddProjectsToSessionView(APIView):
    def post(self, request):
        projects = request.data.get('projects', [])
        SessionManager.add_projects_to_session(request, projects)
        return Response({'message': 'Projects added to session'}, status=status.HTTP_200_OK)
    

class GetSessionDataView(APIView):
    def get(self, request):
        session_data = request.session.get('selected_projects', [])
        return Response({'selected_projects': session_data}, status=status.HTTP_200_OK)    