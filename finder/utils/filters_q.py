import re
from django.db.models import Q

from finder.models import AccountingData
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
    print('banix')
    q_objects = Q()
    for value in values:
        if search_by_code:
            q_objects &= Q(code__startswith=value)
        elif search_by_comment:
            q_objects &= Q(comment__icontains=value)
        else:
            value_q = (Q(title__icontains=value) | 
            Q(comment__icontains=value) | 
            Q(article__icontains=value) | 
            Q(party__icontains=value))
            
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



def get_tn_kd(string, search_by_kd=False):
    """
    Ищет в AccountingData по строке и возвращает список accounting_code для основного поиска
    """
    if not search_by_kd:
        return []
    
    clean_string = ' '.join(string.split()).strip()
    if not clean_string:
        return []
    
    # Сначала ищем точное совпадение в accounting_code
    accounting_codes = list(AccountingData.objects.filter(
        accounting_code__iexact=clean_string
    ).values_list('accounting_code', flat=True).distinct())
    
    # Если не нашли в accounting_code, ищем в nomenclature_kd
    if not accounting_codes:
        accounting_codes = list(AccountingData.objects.filter(
            nomenclature_kd__iexact=clean_string
        ).values_list('accounting_code', flat=True).distinct())
    
    # Если все еще не нашли, пробуем поиск по отдельным словам
    if not accounting_codes and len(clean_string.split()) > 1:
        search_terms = clean_string.split()
        for term in search_terms:
            term = term.strip()
            if term:
                # Ищем в accounting_code
                codes_from_code = list(AccountingData.objects.filter(
                    accounting_code__iexact=term
                ).values_list('accounting_code', flat=True).distinct())
                if codes_from_code:
                    accounting_codes.extend(codes_from_code)
                
                # Ищем в nomenclature_kd  
                codes_from_kd = list(AccountingData.objects.filter(
                    nomenclature_kd__iexact=term
                ).values_list('accounting_code', flat=True).distinct())
                if codes_from_kd:
                    accounting_codes.extend(codes_from_kd)
    
    return list(set(accounting_codes))  # Убираем дубликаты
