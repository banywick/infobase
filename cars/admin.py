# cars/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum
from .models import InventoryItem, Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Админка для управления местами хранения"""
    list_display = ['name', 'code', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code', 'description']
    ordering = ['name']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'code', 'description')
        }),
        ('Статус', {
            'fields': ('is_active',)
        }),
        ('Системные поля', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['created_at', 'updated_at']

class ChildInline(admin.TabularInline):
    """Inline для отображения дочерних позиций"""
    model = InventoryItem
    fk_name = 'parent'
    extra = 0
    fields = ['number', 'arrival_date', 'article', 'name', 'location', 'quantity', 'comment']
    show_change_link = True
    can_delete = True
    ordering = ['created_at']
    verbose_name = "Комплектующая"
    verbose_name_plural = "Комплектующие"
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('created_at')


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    """Админка для учета материальных ценностей"""
    
    # Отображаемые поля в списке
    list_display = [
        'number', 'article', 'name', 'location', 
        'quantity', 'has_children_display', 'children_count', 
        'created_at', 'updated_at', 'actions_display'
    ]
    
    # Фильтры в правой колонке
    list_filter = [
        'arrival_date', 'location', 'created_at', 'updated_at',
        ('parent', admin.EmptyFieldListFilter)
    ]
    
    # Поля для поиска
    search_fields = [
        'number', 'article', 'name', 'location', 'comment'
    ]
    
    # Сортировка по умолчанию
    ordering = ['-created_at']
    
    # Количество записей на странице
    list_per_page = 50
    
    # Поля только для чтения
    readonly_fields = ['created_at', 'updated_at', 'children_count', 'has_children_display']
    
    # Поля для редактирования
    fieldsets = (
        ('Документ', {
            'fields': ('number', 'arrival_date')
        }),
        ('Товар', {
            'fields': ('article', 'name', 'location', 'quantity')
        }),
        ('Иерархия', {
            'fields': ('parent', 'children_count', 'has_children_display'),
            'classes': ('collapse',)
        }),
        ('Дополнительно', {
            'fields': ('comment',)
        }),
        ('Системные поля', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    # Inline для детей
    inlines = [ChildInline]
    
    # Действия
    actions = ['delete_selected', 'export_selected']
    
    # ===== МЕТОДЫ ДЛЯ ОТОБРАЖЕНИЯ =====
    
    def has_children_display(self, obj):
        """Отображение наличия детей в виде иконки"""
        if obj.children.exists():
            count = obj.children.count()
            return format_html(
                '<span style="color: #10b981; font-weight: bold;">✅ Есть ({})</span>',
                count
            )
        return format_html('<span style="color: #9ca3af;">—</span>')
    has_children_display.short_description = "Комплектующие"
    
    def children_count(self, obj):
        """Количество детей"""
        return obj.children.count()
    children_count.short_description = "Кол-во компл."
    
    def actions_display(self, obj):
        """Кнопки действий"""
        # Ссылка на добавление ребенка
        add_child_url = reverse('admin:cars_inventoryitem_add') + f'?parent={obj.id}'
        
        # Ссылка на просмотр детей
        children_url = reverse('admin:cars_inventoryitem_changelist') + f'?parent__id__exact={obj.id}'
        
        return format_html(
            '<div style="display: flex; gap: 5px;">'
            '<a href="{}" style="color: #10b981; text-decoration: none;" title="Добавить комплектующую">➕</a>'
            '<a href="{}" style="color: #3b82f6; text-decoration: none;" title="Показать комплектующие">👁️</a>'
            '</div>',
            add_child_url,
            children_url
        )
    actions_display.short_description = "Действия"
    
    # ===== МЕТОДЫ ДЛЯ ПОИСКА =====
    
    def get_search_results(self, request, queryset, search_term):
        """Расширенный поиск с учетом детей"""
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )
        
        if search_term:
            # Ищем по номеру ТН у детей
            child_numbers = InventoryItem.objects.filter(
                number__icontains=search_term
            ).values_list('parent_id', flat=True)
            
            # Ищем по артикулу у детей
            child_articles = InventoryItem.objects.filter(
                article__icontains=search_term
            ).values_list('parent_id', flat=True)
            
            # Добавляем родителей найденных детей
            parent_ids = set(list(child_numbers) + list(child_articles))
            if parent_ids:
                queryset = queryset | InventoryItem.objects.filter(id__in=parent_ids)
        
        return queryset, use_distinct
    
    # ===== ДЕЙСТВИЯ =====
    
    def export_selected(self, request, queryset):
        """Экспорт выбранных записей в CSV"""
        import csv
        from django.http import HttpResponse
        from datetime import datetime
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response.write('\ufeff')  # BOM для Excel
        response['Content-Disposition'] = f'attachment; filename="export_{datetime.now().strftime("%Y%m%d_%H%M")}.csv"'
        
        writer = csv.writer(response, delimiter=';')
        writer.writerow(['№', '№ ТН, ТТН', 'Дата', 'Артикул', 'Наименование', 'Место', 'Кол-во', 'Комментарий'])
        
        counter = 1
        for item in queryset:
            writer.writerow([
                counter,
                item.number or '',
                item.arrival_date.strftime('%d.%m.%Y') if item.arrival_date else '',
                item.article or '',
                item.name or '',
                item.location or '',
                item.quantity or 0,
                item.comment or ''
            ])
            counter += 1
        
        self.message_user(request, f'Экспортировано {queryset.count()} записей')
        return response
    export_selected.short_description = "Экспортировать выбранные"
    
    # ===== КАСТОМНЫЙ FILTER =====
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Аннотируем количество детей для сортировки
        return qs.annotate(
            children_count_annotated=Count('children')
        )
    
    # ===== АДМИНСКИЕ НАСТРОЙКИ =====
    
    # Настройка отображения в заголовке
    def get_list_display(self, request):
        if request.user.is_superuser:
            return self.list_display
        # Для обычных пользователей скрываем некоторые поля
        return ['id', 'number', 'article', 'name', 'location', 'quantity', 'created_at']
    
    # Настройка доступных действий
    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            # Для обычных пользователей отключаем удаление
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions


# ===== ДОПОЛНИТЕЛЬНЫЕ НАСТРОЙКИ =====

# Настройка заголовка админки
admin.site.site_header = "Система учета МЦ"
admin.site.site_title = "Учет материальных ценностей"
admin.site.index_title = "Панель управления"