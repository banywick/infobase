from django.db.models import Q, Sum
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView
from django.views.generic import TemplateView
from rest_framework import generics, status

from finder.models import Remains
from .utils.article_utils import check_article
from .serializers import HistorySerializer, SahrDataTableSerializer
from .models import *
from rest_framework.response import Response



class BasePositionView(generics.GenericAPIView):
    queryset = Data_Table.objects.all()
    serializer_class = SahrDataTableSerializer
    lookup_field = 'id'

class SahrView(TemplateView):
    """Главная страница САХР"""
    template_name = 'sahr/index.html'

class SahrArchiveView(TemplateView):
    """Страница с архивом"""
    template_name = 'sahr/archive.html'

class AllArchiveRemovePosition(generics.ListAPIView):
    """Все позиции с архива"""

    queryset = Deleted.objects.all()
    serializer_class = SahrDataTableSerializer


class SahrFindFilterArchive(APIView):
    """Поиск в архиве"""
    def post(self, request, *args, **kwargs):
        query = request.data.get('query', '')

        # Создаем Q-объекты для каждого поля
        article = Q(article__icontains=query)
        party = Q(party__icontains=query)
        address = Q(address__icontains=query)

        # Объединяем Q-объекты с помощью логического "или"
        combined_query = article | party | address

        # Фильтруем данные в таблице
        results = Deleted.objects.filter(combined_query)

        # Возвращаем результаты в формате JSON
        return Response(results.values())


class SahrFindFilter(APIView):
    def post(self, request, *args, **kwargs):
        query = request.data.get('query', '')

        # Создаем Q-объекты для каждого поля
        article = Q(article__icontains=query)
        party = Q(party__icontains=query)
        address = Q(address__icontains=query)

        # Объединяем Q-объекты с помощью логического "или"
        combined_query = article | party | address

        # Фильтруем данные в таблице
        results = Data_Table.objects.filter(combined_query)

        # Возвращаем результаты в формате JSON
        return Response(results.values())
    
    
    
class GetSahrAllPositions(BasePositionView, generics.ListAPIView):
    pass



class AddPositions(BasePositionView ,CreateAPIView):
    def create(self, request, *args, **kwargs):
        # Создаем изменяемую копию request.data
        data = request.data.copy()
        print(data)

        # Получаем id из данных
        instance_id = data.get('id')
        
        try:
            # Находим экземпляр модели Remains по id
            instance = Remains.objects.get(id=instance_id)
            
            # Получаем артикул из найденного экземпляра
            article = instance.article
            
            # Заменяем артикул в передаваемых данных
            data['article'] = article
            
            # Используем ваш сериализатор для обработки данных
            serializer = SahrDataTableSerializer(data=data)
            serializer.is_valid(raise_exception=True)  # Проверяем валидность данных
            
            # Сохраняем данные
            serializer.save()
            
            # Возвращаем ответ
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Data_Table.DoesNotExist:
            # Если экземпляр не найден, возвращаем ошибку
            return Response({"error": "Data_Table instance not found"}, status=status.HTTP_404_NOT_FOUND)


class EditPosition(BasePositionView, generics.RetrieveUpdateAPIView):
    pass
    
    
class RemovePosition(BasePositionView, DestroyAPIView):

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'successfully deleted'}, status=status.HTTP_200_OK)



class HistoryListView(ListAPIView):
    serializer_class = HistorySerializer

    def get_queryset(self):
        data_table_id = self.kwargs['id']
        return History.objects.filter(data_table_id=data_table_id)
    

class CheckArticleAPIView(APIView):
    def get(self, request, art):
        """Проверка, есть ли такой артикул в базе данных."""
        result = check_article(art)
        if result:
            return Response(result)
        return Response({"error": "Товара нет в базе"}, status=status.HTTP_404_NOT_FOUND)   
    