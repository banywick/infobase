import re
from django.db.models import Q

from finder.utils.standarts import find_standard_values
from .metiz import process_metiz_value

def get_current_projects(request):
    """
    Получает текущие проекты из сессии пользователя.
    Поддерживает как старый (dict), так и новый (list) форматы.
    
    Args:
        request (HttpRequest): Объект запроса.
    
    Returns:
        list: Список значений текущих проектов.
    """
    current_projects = request.session.get('selected_projects', [])
    
    # Если это новый формат (список словарей)
    if isinstance(current_projects, list):
        # Возвращаем список названий проектов
        return [project['project'] for project in current_projects]
    

# q обекты для фильтрации проектоов
def create_q_objects(values, field_name):
    """
    Создает Q-объекты для фильтрации на основе списка значений и имени поля.

    Args:
        values (list): Список значений для фильтрации.
        field_name (str): Имя поля, по которому будет производиться фильтрация.

    Returns:
        Q: Q-объект для фильтрации.
    """
    q_objects = Q()
    for value in values:
        print(value)
        q_objects |= Q(**{f'{field_name}': value})
    return q_objects

# q обекты для фильтрации значений с инпута
def create_q_objects_for_query(values, search_by_code=False, search_by_comment=False, search_by_analog=False):
    q_objects = Q()
    for value in values:
        if search_by_code:
            q_objects &= Q(code__startswith=value)
        elif search_by_comment:
            q_objects &= Q(comment__icontains=value)
        else:
            value_q = Q(title__icontains=value) | Q(comment__icontains=value)
            
            if search_by_analog:
                standard_values = find_standard_values(value)
                if standard_values:
                    standard_q = Q()
                    for std_value in standard_values:
                        standard_q |= Q(title__icontains=std_value)
                    value_q |= standard_q
            
            metiz_q = process_metiz_value(value)
            if metiz_q:
                value_q |= metiz_q
            
            q_objects &= value_q
    
    return q_objects


def get_analogs_list(search_terms, search_by_analog=False):
    """
    Возвращает список аналогов для переданных поисковых терминов.
    
    Args:
        search_terms (list): Список терминов для поиска аналогов
        search_by_analog (bool): Флаг поиска по аналогам
    
    Returns:
        list: Список найденных аналогов (пустой список, если search_by_analog=False)
    """
    analogs_list = []
    
    if not search_by_analog:
        return analogs_list
    
    for term in search_terms:
        standard_values = find_standard_values(term)
        if standard_values:
            analogs_list.extend(standard_values)
    
    # Удаляем дубликаты, если они не нужны
    analogs_list = list(set(analogs_list)) if analogs_list else []
    
    return analogs_list



