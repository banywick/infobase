from django.db.models import Sum
from finder.models import Remains

def check_article(art):
    """Проверка, есть ли такой артикул в базе данных."""
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