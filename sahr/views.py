from django.db.models import Q, Sum
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView
from django.views.generic import TemplateView
from rest_framework import generics, status

from finder.models import Remains
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
    pass


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
        article = Remains.objects.filter(article__icontains=art).first()
        if article:
            total_quantity = Remains.objects.filter(article=article).aggregate(sum_quantity=Sum('quantity'))['sum_quantity']
            all_party = Remains.objects.filter(article=article)
            party = {i: p.party for i, p in enumerate(all_party)}
            title = article.title
            unit = article.base_unit
            art_product = article.article
            project = article.project
            id = article.id
            total_quantity = f'{total_quantity:.2f}'
            return Response({
                "title": title,
                "id": id,
                "party": party,
                'total_quantity': total_quantity,
                'unit': unit,
                'article': art_product,
                "project": project
            })
        return Response({"error": "Товара нет в базе"}, status=status.HTTP_404_NOT_FOUND)    
    