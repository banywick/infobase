# services/search_service.py
from urllib.parse import unquote
from rest_framework import status
from finder.models import AccountingData
from finder.serializers import AccountingDataSerializer


class SearchService:
    """
    Сервис для выполнения поисковых операций в AccountingData
    """
    
    @staticmethod
    def extract_search_term(request, url_param=None):
        """
        Извлекает поисковый термин из запроса.
        Приоритет: тело запроса > URL параметр
        
        Args:
            request: HTTP request объект
            url_param: Поисковая строка из URL (опционально)
            
        Returns:
            str: Поисковый термин или None если не найден
        """
        # Проверяем тело запроса
        if request.data and 'search_string' in request.data:
            return request.data['search_string']
        
        # Проверяем URL параметр
        if url_param:
            return unquote(url_param)
        
        return None
    
    @classmethod
    def search_by_nomenclature(cls, search_term):
        """
        Выполняет поиск по полю nomenclature_kd
        
        Args:
            search_term: Строка для поиска
            
        Returns:
            QuerySet: Результаты поиска
        """
        if not search_term:
            return AccountingData.objects.none()
        
        return AccountingData.objects.filter(
            nomenclature_kd__icontains=search_term
        )
    
    @classmethod
    def get_search_results(cls, search_term):
        """
        Получает результаты поиска и их количество
        
        Args:
            search_term: Строка для поиска
            
        Returns:
            dict: Словарь с результатами поиска
        """
        results = cls.search_by_nomenclature(search_term)
        serializer = AccountingDataSerializer(results, many=True)
        
        return {
            'search_string': search_term,
            'matches_found': results.count(),
            'data': serializer.data
        }
    
    @classmethod
    def process_search_request(cls, request, url_param=None):
        """
        Полный цикл обработки поискового запроса
        
        Args:
            request: HTTP request объект
            url_param: Поисковая строка из URL (опционально)
            
        Returns:
            tuple: (search_results_dict, error_message, status_code)
        """
        search_term = cls.extract_search_term(request, url_param)
        
        if not search_term:
            return None, 'Не передана строка для поиска', status.HTTP_400_BAD_REQUEST
        
        results = cls.get_search_results(search_term)
        return results, None, status.HTTP_200_OK