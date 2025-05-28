from finder.models import Standard, StandardValue

from django.core.cache import cache

# def find_standard_values(value):
#     cache_key = f"standard_values:{value}"
#     cached = cache.get(cache_key)
    
#     if cached is not None:
#         return cached
    
#     try:
#         standard_value = StandardValue.objects.select_related('standard').get(value=value)
#         values = list(
#             StandardValue.objects
#             .filter(standard=standard_value.standard)
#             .values_list('value', flat=True)
#         )
#         cache.set(cache_key, values, timeout=60*60*24)  # Кеш на 24 часа
#         return values
#     except StandardValue.DoesNotExist:
#         cache.set(cache_key, None, timeout=60*60*24)
#         return None
    

def find_standard_values(value):
    """
    Находит все стандартные значения из того же стандарта, что и переданное значение
    без использования кеширования.

    Args:
        value (str): Значение для поиска в стандартных значениях
        
    Returns:
        list: Список связанных стандартных значений или None если не найдено
    """
    try:
        # Находим исходное стандартное значение
        standard_value = StandardValue.objects.select_related('standard').get(value=value)
        
        # Получаем все значения из того же стандарта
        values = list(
            StandardValue.objects
            .filter(standard=standard_value.standard)
            .values_list('value', flat=True)
        )
        
        return values
        
    except StandardValue.DoesNotExist:
        # Если значение не найдено в стандартах
        return None