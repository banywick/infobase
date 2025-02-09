from django.db.models import Sum
from finder.models import Remains

def check_article(art):
    """
    Проверяет наличие артикула в базе данных и возвращает информацию о найденном артикуле.

    Функция ищет артикул в базе данных модели `Remains`. Если артикул найден, возвращает словарь
    с информацией о товаре, включая название, идентификатор, партии, общее количество, базовую единицу измерения,
    артикул и проект. Если артикул не найден, возвращает `None`.

    Параметры:
    ----------
    art : str
        Артикул, который необходимо найти в базе данных.

    Возвращает:
    ----------
    dict or None
        Словарь с информацией о товаре, если артикул найден. Содержит следующие ключи:
        - "title" (str): Название товара.
        - "id" (int): Идентификатор товара.
        - "party" (dict): Словарь с партиями товара, где ключи — индексы, а значения — номера партий.
        - "total_quantity" (str): Общее количество товара в формате строки с двумя знаками после запятой.
        - "base_unit" (str): Базовая единица измерения товара.
        - "article" (str): Артикул товара.
        - "project" (str): Проект, к которому относится товар.
        Если артикул не найден, возвращает `None`.
    """
    article = Remains.objects.filter(article__icontains=art).first()
    if article:
        total_quantity = Remains.objects.filter(article=article).aggregate(sum_quantity=Sum('quantity'))['sum_quantity']
        all_party = Remains.objects.filter(article=article)
        party = {i: p.party for i, p in enumerate(all_party)}
        title = article.title
        unit = article.base_unit
        art_product = article.article
        project = article.project
        id = article.id
        total_quantity = f'{total_quantity:.2f}'
        return {
            "title": title,
            "id": id,
            "party": party,
            'total_quantity': total_quantity,
            'base_unit': unit,
            'article': art_product,
            "project": project
        }
    return None