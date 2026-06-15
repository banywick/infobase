# inventory_app/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import InventoryItem
from finder.models import Remains
import json
import logging

logger = logging.getLogger(__name__)




def table_view(request):
    """Главная страница с таблицей"""
    items = InventoryItem.objects.filter(parent__isnull=True).order_by('-id')
    
    # Получаем уникальные места хранения
    locations = InventoryItem.objects.exclude(location__isnull=True).exclude(location='').values_list('location', flat=True).distinct()
    default_locations = ['Площадка Хранилища №30', 'Склад №5', 'Склад №12', 'Открытая площадка 1']
    all_locations = list(set(list(locations) + default_locations))
    all_locations.sort()
    
    context = {
        'items': items,
        'locations': all_locations,
    }
    return render(request, 'cars/index.html', context)


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
            location=data.get('location', ''),
            quantity=data.get('quantity'),
            comment=data.get('comment', ''),
            parent_id=data.get('parent') or None
        )
        
        return JsonResponse({
            'success': True,
            'id': item.id,
            'message': 'Строка успешно сохранена'
        })
        
    except Exception as e:
        logger.error(f"Error saving row: {e}")
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
        item.location = data.get('location', item.location)
        item.quantity = data.get('quantity', item.quantity)
        item.comment = data.get('comment', item.comment)
        item.save()
        
        return JsonResponse({
            'success': True,
            'id': item.id,
            'message': 'Строка обновлена'
        })
        
    except Exception as e:
        logger.error(f"Error updating row: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_row(request, item_id):
    """Удаление строки и всех её детей"""
    try:
        item = get_object_or_404(InventoryItem, id=item_id)
        # Удаляем рекурсивно всех детей
        item.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Строка удалена'
        })
        
    except Exception as e:
        logger.error(f"Error deleting row: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def get_locations(request):
    """Получение списка уникальных мест хранения"""
    try:
        locations = InventoryItem.objects.exclude(location__isnull=True).exclude(location='').values_list('location', flat=True).distinct()
        default_locations = ['Площадка Хранилища №30', 'Склад №5', 'Склад №12', 'Открытая площадка 1']
        all_locations = list(set(list(locations) + default_locations))
        all_locations.sort()
        
        return JsonResponse({'success': True, 'locations': all_locations})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def add_child(request):
    """Добавление дочерней позиции"""
    try:
        data = json.loads(request.body)
        parent_id = data.get('parent_id')
        article = data.get('article')
        name = data.get('name', article)
        quantity = data.get('quantity', 1)
        
        parent = InventoryItem.objects.get(id=parent_id)
        
        child = InventoryItem.objects.create(
            number=parent.number,
            arrival_date=parent.arrival_date,
            location=parent.location,
            article=article,
            name=name,
            quantity=quantity,
            comment=data.get('comment', ''),
            parent=parent
        )
        
        return JsonResponse({
            'success': True,
            'id': child.id,
            'message': 'Дочерняя позиция добавлена'
        })
    except InventoryItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Родительская позиция не найдена'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)