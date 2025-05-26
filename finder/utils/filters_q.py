import re
from django.db.models import Q
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
def create_q_objects_for_query(values, search_by_code, search_by_comment):
    q_objects = Q()
    
    for value in values:
        if search_by_code:
            q_objects &= Q(code__startswith=value)
        elif search_by_comment:
            q_objects &= Q(comment__icontains=value)
        else:
            # Основное условие: слово должно быть в title если нет title
            # ищем code
            value_q = Q(title__icontains=value) | Q(comment__icontains=value)
            
            # Если это метиз - добавляем его варианты через ИЛИ
            metiz_q = process_metiz_value(value)
            if metiz_q:
                value_q |= metiz_q  # Комбинируем через или
            
            q_objects &= value_q
    
    return q_objects
