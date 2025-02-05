from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, DestroyAPIView, RetrieveUpdateAPIView
from django.views.generic import TemplateView
from rest_framework import generics, status
from .serializers import SahrDataTableSerializer
from .models import *
from rest_framework.response import Response



class BasePositionView(generics.GenericAPIView):
    queryset = Data_Table.objects.all()
    serializer_class = SahrDataTableSerializer
    lookup_field = 'id'

class SahrView(TemplateView):
    template_name = 'sahr/index.html'


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



class AddPositions(BasePositionView ,CreateAPIView):
    pass


class EditPosition(BasePositionView, generics.RetrieveUpdateAPIView):
    pass
    
    
class RemovePosition(BasePositionView, DestroyAPIView):

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'successfully deleted'}, status=status.HTTP_200_OK)



class ArchiveRemovePosition(generics.ListAPIView):
    queryset = Deleted.objects.all()
    serializer_class = SahrDataTableSerializer


class HistiryEditPositions(generics.ListAPIView):
    queryset = Deleted.objects.all()
    serializer_class = SahrDataTableSerializer