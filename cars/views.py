# inventory_app/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import InventoryItem
import json
from finder.models import Remains



def table_view(request):
    """Главная страница с таблицей"""
    items = InventoryItem.objects.all().order_by('-id')
    return render(request, 'cars/index.html', {'items': items})


@csrf_exempt
def get_details_by_article(request, article):
    """Ваш существующий API для получения данных по артикулу"""
    try:
        # Поиск в таблице Remains
        remains = Remains.objects.filter(article=article).first()
        
        if remains:
            # Формируем ответ в том формате, который вы показали
            data = {
                "id": remains.id,
                "article": remains.article,
                "title": remains.name,  # или remains.title, зависит от вашей модели
                "base_unit": remains.base_unit if hasattr(remains, 'base_unit') else "шт",
                "one_project": remains.one_project if hasattr(remains, 'one_project') else "",
                "status_one_project": "gray",
                "total_quantity": remains.total_quantity if hasattr(remains, 'total_quantity') else 0,
                "total_quantity_by_project": remains.total_quantity if hasattr(remains, 'total_quantity') else 0,
                "party": [],
                "details_any_projects": [],
                "total_sum_any_projects": 0
            }
            return JsonResponse(data)
        else:
            return JsonResponse(
                {"error": f"Артикул {article} не найден"},
                status=404
            )
            
    except Exception as e:
        return JsonResponse(
            {"error": str(e)},
            status=500
        )


@csrf_exempt
@require_http_methods(["POST"])
def save_row(request):
    """Сохранение новой строки"""
    try:
        data = json.loads(request.body)
        
        item = InventoryItem.objects.create(
            number=data.get('number', ''),
            arrival_date=data.get('arrival_date') or None,
            article=data.get('article', ''),
            name=data.get('name', ''),
            quantity=data.get('quantity'),
            unit=data.get('unit', ''),
            comment=data.get('comment', '')
        )
        
        return JsonResponse({
            'success': True,
            'id': item.id,
            'message': 'Строка успешно сохранена'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def update_row(request, item_id):
    """Обновление существующей строки"""
    try:
        item = get_object_or_404(InventoryItem, id=item_id)
        data = json.loads(request.body)
        
        item.number = data.get('number', item.number)
        item.arrival_date = data.get('arrival_date') or item.arrival_date
        item.article = data.get('article', item.article)
        item.name = data.get('name', item.name)
        item.quantity = data.get('quantity', item.quantity)
        item.unit = data.get('unit', item.unit)
        item.comment = data.get('comment', item.comment)
        item.save()
        
        return JsonResponse({
            'success': True,
            'id': item.id,
            'message': 'Строка успешно обновлена'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_row(request, item_id):
    """Удаление строки"""
    try:
        item = get_object_or_404(InventoryItem, id=item_id)
        item.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Строка успешно удалена'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


def get_rows(request):
    """Получение всех записей (для AJAX)"""
    items = InventoryItem.objects.all().order_by('-id')
    data = []
    
    for item in items:
        data.append({
            'id': item.id,
            'number': item.number,
            'arrival_date': item.arrival_date.strftime('%Y-%m-%d') if item.arrival_date else None,
            'article': item.article,
            'name': item.name,
            'quantity': item.quantity,
            'unit': item.unit,
            'comment': item.comment,
        })
    
    return JsonResponse({'success': True, 'data': data})


def get_row(request, item_id):
    """Получение одной записи"""
    try:
        item = get_object_or_404(InventoryItem, id=item_id)
        data = {
            'id': item.id,
            'number': item.number,
            'arrival_date': item.arrival_date.strftime('%Y-%m-%d') if item.arrival_date else None,
            'article': item.article,
            'name': item.name,
            'quantity': item.quantity,
            'unit': item.unit,
            'comment': item.comment,
        }
        return JsonResponse({'success': True, 'data': data})
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=404)