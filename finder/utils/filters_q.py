from django.db.models import Q
from .metiz import process_metiz_query

def get_current_projects(request):
    """
    Получает текущие проекты из сессии пользователя.
    преобразовывает dict в list

    Args:
        request (HttpRequest): Объект запроса.

    Returns:
        list: Список значений текущих проектов.
    """
    current_projects = request.session.get('selected_projects', {})
    return list(current_projects.values())

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
        q_objects |= Q(**{f'{field_name}': value})
    return q_objects

def create_q_objects_for_query(values, search_by_code, search_by_comment):
    """
    Создает Q-объекты для фильтрации на основе запроса пользователя.

    Args:
        values (list): Список значений для фильтрации.
        search_by_code (bool): Флаг для поиска по коду.
        search_by_comment (bool): Флаг для поиска по комментарию.

    Returns:
        Q: Q-объект для фильтрации.
    """
    q_objects = Q()
    for value in values:
        current_q = Q()
        if search_by_code:
            q_objects &= Q(code__startswith=value)
            return q_objects
        if search_by_comment:
            q_objects &= Q(comment__icontains=value)
            return q_objects

        # По умолчанию ищем по title или comment
        current_q &= (Q(title__icontains=value)
                    | Q(comment__icontains=value)
                    | Q(article__icontains=value))

        # Дополнительная логика для метизов
        metiz_all, replace_a = process_metiz_query(value)
        current_q |= metiz_all
        current_q |= replace_a

        q_objects &= current_q
    return q_objects
