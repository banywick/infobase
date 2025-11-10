import re
from django.db.models import Q




def process_metiz_value(value):
    """
    Обрабатывает специальные форматы для метизов.
    Для шаблона *number (например, *10) ищет все варианты с разделителями.
    """
    value = value.strip()

    # Если значение обернуто в две звезды (например, *4,3*)
    if value.startswith('*') and value.endswith('*'):
        num = value[1:-1]  # Убираем звезды
        num_dot = num.replace(',', '.')
        num_comma = num.replace('.', ',')

        # Разделители
        separators = ['А', 'A', 'В', 'B', 'М', 'M', 'Ф', ' ']

        q = Q()
        for sep in separators:
            # Ищем: А4,3 или A4.3 и т.д.
            q |= Q(title__iregex=rf"\y{re.escape(sep)}{re.escape(num)}\y")
            q |= Q(title__iregex=rf"\y{re.escape(sep)}{re.escape(num_dot)}\y")
            q |= Q(title__iregex=rf"\y{re.escape(sep)}{re.escape(num_comma)}\y")

        # Ищем просто 4,3 или 4.3
        q |= Q(title__iregex=rf"\y{re.escape(num)}\y")
        q |= Q(title__iregex=rf"\y{re.escape(num_dot)}\y")
        q |= Q(title__iregex=rf"\y{re.escape(num_comma)}\y")

        return q

    # Если значение обернуто в одну звезду (например, *8)
    elif value.startswith('*'):
        num = value[1:]  # Убираем звезду

        # Проверяем, что это целое число
        if not re.fullmatch(r"\d+", num):
            return Q()  # Если не целое число, возвращаем пустой запрос

        # Разделители
        separators = ['А', 'A', 'В', 'B', 'М', 'M', 'Ф', ' ']

        q = Q()
        for sep in separators:
            # Ищем только целые числа: А8, M8 и т.д.
            # Используем отрицательный просмотр, чтобы исключить 8.4, 8,4
            q |= Q(title__iregex=rf"\y{re.escape(sep)}{re.escape(num)}\y(?![,\.]\d)")

        # Ищем просто 8, но только если это целое число
        q |= Q(title__iregex=rf"\y{re.escape(num)}\y(?![,\.]\d)")

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



