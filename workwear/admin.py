# backend/workwear/admin.py

import pandas as pd
from django.contrib import admin
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import path
from django.template.response import TemplateResponse
from .models import Employee, WorkwearCategory, WorkwearItem, WorkwearHistory
import logging

logger = logging.getLogger(__name__)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'department', 'position', 'is_active', 'created_at']
    list_filter = ['department', 'position', 'is_active']
    search_fields = ['first_name', 'last_name', 'patronymic', 'department', 'position']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Персональная информация', {
            'fields': ('last_name', 'first_name', 'patronymic')
        }),
        ('Работа', {
            'fields': ('department', 'position', 'is_active')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    change_list_template = 'admin/workwear/employee/change_list.html'
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'ФИО'
    get_full_name.admin_order_field = 'last_name'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-excel/', self.import_excel_view, name='import_excel'),
            path('process-excel/', self.process_excel_view, name='process_excel'),
        ]
        return custom_urls + urls
    
    def import_excel_view(self, request):
        """Страница загрузки Excel файла"""
        context = {
            'title': 'Импорт сотрудников из Excel',
            'opts': self.model._meta,
            'has_change_permission': self.has_change_permission(request),
            'app_label': self.model._meta.app_label,
            'model_name': self.model._meta.model_name,
        }
        return TemplateResponse(request, 'admin/workwear/employee/import_excel.html', context)
    
    def process_excel_view(self, request):
        """Обработка загруженного Excel файла"""
        if request.method != 'POST':
            return redirect('admin:workwear_employee_changelist')
        
        if 'excel_file' not in request.FILES:
            messages.error(request, 'Файл не выбран')
            return redirect('admin:workwear_employee_changelist')
        
        excel_file = request.FILES['excel_file']
        
        if not excel_file.name.endswith(('.xlsx', '.xls')):
            messages.error(request, 'Поддерживаются только файлы .xlsx и .xls')
            return redirect('admin:workwear_employee_changelist')
        
        try:
            df = pd.read_excel(excel_file)
            
            # Проверка обязательных колонок
            required_columns = ['Фамилия', 'Имя']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                messages.error(
                    request, 
                    f'В файле отсутствуют обязательные колонки: {", ".join(missing_columns)}. '
                    f'Доступные колонки: {", ".join(df.columns)}'
                )
                return redirect('admin:workwear_employee_changelist')
            
            created_count = 0
            skipped_count = 0
            error_count = 0
            errors = []
            created_names = []
            
            for index, row in df.iterrows():
                try:
                    last_name = str(row.get('Фамилия', '')).strip()
                    first_name = str(row.get('Имя', '')).strip()
                    patronymic = str(row.get('Отчество', '')).strip() if 'Отчество' in row else ''
                    department = str(row.get('Отдел', '')).strip() if 'Отдел' in row else ''
                    position = str(row.get('Должность', '')).strip() if 'Должность' in row else ''
                    
                    # Проверка обязательных полей
                    if not last_name or not first_name:
                        errors.append(
                            f'Строка {index + 2}: Не заполнены обязательные поля '
                            f'(Фамилия: "{last_name}", Имя: "{first_name}")'
                        )
                        error_count += 1
                        continue
                    
                    # Нормализация отчества
                    if patronymic.lower() in ['нет', '-', 'nan', 'none', '']:
                        patronymic = None
                    
                    # Проверка на дубликат
                    duplicate = Employee.objects.filter(
                        last_name__iexact=last_name,
                        first_name__iexact=first_name,
                        patronymic__iexact=patronymic if patronymic else None
                    ).exists()
                    
                    if duplicate:
                        skipped_count += 1
                        continue
                    
                    # Создание сотрудника
                    employee = Employee.objects.create(
                        last_name=last_name,
                        first_name=first_name,
                        patronymic=patronymic if patronymic else None,
                        department=department,
                        position=position,
                        is_active=True
                    )
                    
                    created_count += 1
                    created_names.append(employee.get_full_name())
                    
                except Exception as e:
                    errors.append(f'Строка {index + 2}: {str(e)}')
                    error_count += 1
            
            # Формируем сообщение
            if created_count > 0:
                messages.success(
                    request, 
                    f'✅ Создано сотрудников: {created_count}'
                )
                if created_names:
                    preview = ', '.join(created_names[:5])
                    if len(created_names) > 5:
                        preview += f' и еще {len(created_names) - 5}'
                    messages.info(request, f'Добавлены: {preview}')
            
            if skipped_count > 0:
                messages.info(request, f'⏭️ Пропущено (уже существуют): {skipped_count}')
            
            if error_count > 0:
                messages.warning(request, f'❌ Ошибок: {error_count}')
                if errors:
                    messages.error(request, 'Детали:\n' + '\n'.join(errors[:10]))
                    if len(errors) > 10:
                        messages.info(request, f'... и еще {len(errors) - 10} ошибок')
            
            if created_count == 0 and skipped_count == 0 and error_count == 0:
                messages.warning(request, 'Нет данных для импорта')
            
        except Exception as e:
            logger.error(f'Error importing Excel: {str(e)}')
            messages.error(request, f'Ошибка при обработке файла: {str(e)}')
        
        return redirect('admin:workwear_employee_changelist')


@admin.register(WorkwearCategory)
class WorkwearCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'standard_lifespan', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(WorkwearItem)
class WorkwearItemAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'employee', 'category', 
        'issue_date', 'expiration_date', 'get_status_display_colored'
    ]
    list_filter = ['category', 'is_active', 'employee__department']
    search_fields = ['name', 'employee__last_name', 'employee__first_name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'expiration_date'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('employee', 'category', 'name')
        }),
        ('Характеристики', {
            'fields': ('size', 'color')
        }),
        ('Сроки', {
            'fields': ('issue_date', 'expiration_date')
        }),
        ('Дополнительно', {
            'fields': ('is_active', 'notes')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_status_display_colored(self, obj):
        from django.utils.html import format_html
        status = obj.get_status()
        colors = {
            'active': ('#28a745', '✅ Активна'),
            'expiring_soon': ('#ffc107', '⏰ Истекает'),
            'expired': ('#dc3545', '❌ Просрочена'),
        }
        color, text = colors.get(status, ('#6c757d', status))
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, text
        )
    get_status_display_colored.short_description = 'Статус'
    get_status_display_colored.admin_order_field = 'expiration_date'


@admin.register(WorkwearHistory)
class WorkwearHistoryAdmin(admin.ModelAdmin):
    list_display = ['workwear_item', 'action', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['workwear_item__name', 'description']
    readonly_fields = ['created_at']