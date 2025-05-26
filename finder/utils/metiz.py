import re
from django.db.models import Q




def process_metiz_value(value):
    """
    Обрабатывает специальные форматы для метизов.
    Для шаблона *number (например, *10) ищет все варианты с разделителями.
    """
    # Формат *number (шайбы/гайки) - ПРИОРИТЕТНЫЙ случай
    if re.match(r"^\*\d+([,.]\d*)?$", value):
        _, num = value.split('*')  # Разделяем "*10" → ("", "10")
        separators = ['А', 'A', 'В', 'B', 'М', 'M', 'Ф', ' ']
        q = Q()
        for sep in separators:
            q |= Q(title__icontains=f"{sep}{num}")  # Ищем: А10, A10, ..., 10
        return q
    
    # Остальные случаи (number*number, A4/А2) - остаются без изменений
    if re.match(r"^(\d+(\.\d+)?[*]\d+|5f[*]\d+)$", value):
        v1 = value.replace("*", "х")
        v2 = value.replace("*", "x")
        return Q(title__icontains=v1) | Q(title__icontains=v2)
    
    if re.match(r"^[aа][24]\b", value):
        variant = value.replace("а", "a")
        return Q(title__icontains=value) | Q(title__icontains=variant)
    
    return None



