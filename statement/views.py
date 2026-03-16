from urllib.parse import unquote
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from finder.models import AccountingData
from finder.serializers import AccountingDataSerializer



class StatementHome(TemplateView):
    """Главная страница ВК"""

    template_name = 'statement/statement.html'




class Statement(APIView):
    """
    Эндпоинт поддерживает:
    1. POST с JSON телом: {"search_string": "текст"}
    2. POST с строкой в URL: /api/draw_statement/текст/
    """
    
    def post(self, request, search_string=None):
        # Приоритет: тело запроса > URL параметр
        if request.data and 'search_string' in request.data:
            search_term = request.data['search_string']
        elif search_string:
            # Декодируем URL-закодированную строку
            search_term = unquote(search_string)
        else:
            return Response(
                {'error': 'Не передана строка для поиска'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Поиск в базе
        results = AccountingData.objects.filter(
            nomenclature_kd__icontains=search_term
        )
        
        serializer = AccountingDataSerializer(results, many=True)
        
        return Response({
            'search_string': search_term,
            'matches_found': results.count(),
            'data': serializer.data
        })
    