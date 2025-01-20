import re
from django.db.models import Q

def process_metiz_query(value):
    """Обработка специфических случаев для метизов."""
    metiz_all = Q()
    replace_a = Q()

    if re.match(r"^(\d+(\.\d+)?[*]\d+|5f[*]\d+)$", value):
        v1 = value.lower().replace("*", "х")  # Кириллица
        v2 = value.lower().replace("*", "x")  # Латиница
        metiz_all = (
            Q(title__icontains=v1)
            | Q(title__icontains=v2)
            | Q(title__icontains=value)
        )

    if re.match(r"^[aа][24]\b", value):
        variant1 = value.lower().replace("а", "a")  # Меняем кирилицу на латиницу A4, A2
        replace_a = Q(title__icontains=value) | Q(title__icontains=variant1)

    return metiz_all, replace_a