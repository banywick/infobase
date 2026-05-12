# statement/admin.py
from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect, render
from django.contrib import messages
from django.utils.html import format_html
from django.urls import reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.db import transaction
from .models import SMBPathConfig, SMBFileIndex, SMBIndexSchedule
from .tasks import index_smb_files
from celery.result import AsyncResult
import json


@admin.register(SMBPathConfig)
class SMBPathConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'search_path', 'result_path', 'is_active', 'index_status', 'reindex_button']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    actions = ['reindex_selected']
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('reindex-all/', self.admin_site.admin_view(self.reindex_all), name='smbpathconfig_reindex_all'),
            path('reindex/<int:config_id>/', self.admin_site.admin_view(self.reindex_single), name='smbpathconfig_reindex_single'),
            path('check-status/<str:task_id>/', self.admin_site.admin_view(self.check_task_status), name='check_task_status'),
        ]
        return custom_urls + urls
    
    def index_status(self, obj):
        """Показывает статус индексации"""
        file_count = SMBFileIndex.objects.filter(config=obj, is_available=True).count()
        if file_count > 0:
            return format_html(
                '<span style="color: #28a745;">✓ Индексировано: {} файлов</span>',
                file_count
            )
        return format_html(
            '<span style="color: #dc3545;">✗ Не индексировано</span>'
        )
    index_status.short_description = "Статус индекса"
    
    def reindex_button(self, obj):
        return format_html(
            '<a class="button" href="{}">🔄 Индексировать</a>',
            reverse('admin:smbpathconfig_reindex_single', args=[obj.id])
        )
    reindex_button.short_description = "Индексация"
    reindex_button.allow_tags = True
    
    def reindex_all(self, request):
        """Метод для массовой индексации"""
        if request.method == 'POST':
            force = request.POST.get('force', False) == 'true'
            task = index_smb_files.delay(force=force)
            return JsonResponse({
                'task_id': task.id,
                'status': 'started'
            })
        
        context = {
            'title': 'Индексация всех SMB путей',
            'opts': self.model._meta,
            'has_perm': True,
            'configs': SMBPathConfig.objects.filter(is_active=True)
        }
        return render(request, 'admin/statement/reindex_confirmation.html', context)
    
    def reindex_single(self, request, config_id):
        """Индексация одной конфигурации"""
        if request.method == 'POST':
            force = request.POST.get('force', False) == 'true'
            task = index_smb_files.delay(config_id=config_id, force=force)
            return JsonResponse({
                'task_id': task.id,
                'status': 'started'
            })
        
        config = SMBPathConfig.objects.get(id=config_id)
        context = {
            'title': f'Индексация: {config.name}',
            'config': config,
            'opts': self.model._meta,
            'has_perm': True
        }
        return render(request, 'admin/statement/reindex_single_confirmation.html', context)
    
    def check_task_status(self, request, task_id):
        """Проверка статуса задачи индексации"""
        task = AsyncResult(task_id)
        result = {
            'task_id': task_id,
            'status': task.status,
            'ready': task.ready(),
            'result': task.result if task.ready() else None
        }
        return JsonResponse(result)
    
    def reindex_selected(self, request, queryset):
        """Action для массовой индексации выбранных конфигураций"""
        for config in queryset:
            if config.is_active:
                index_smb_files.delay(config_id=config.id, force=False)
        self.message_user(request, f"Запущена индексация для {queryset.count()} конфигураций")
    reindex_selected.short_description = "Запустить индексацию для выбранных"


@admin.register(SMBFileIndex)
class SMBFileIndexAdmin(admin.ModelAdmin):
    list_display = ['filename', 'config', 'file_extension', 'file_size', 'is_available', 'last_checked']
    list_filter = ['config', 'file_extension', 'is_available']
    search_fields = ['filename', 'relative_path', 'file_path']
    readonly_fields = ['file_path', 'relative_path', 'file_size', 'modified_time', 'created_at']
    actions = ['mark_available', 'mark_unavailable', 'delete_selected']
    
    def mark_available(self, request, queryset):
        queryset.update(is_available=True)
        self.message_user(request, f"{queryset.count()} файлов отмечены как доступные")
    mark_available.short_description = "Отметить как доступные"
    
    def mark_unavailable(self, request, queryset):
        queryset.update(is_available=False)
        self.message_user(request, f"{queryset.count()} файлов отмечены как недоступные")
    mark_unavailable.short_description = "Отметить как недоступные"


@admin.register(SMBIndexSchedule)
class SMBIndexScheduleAdmin(admin.ModelAdmin):
    list_display = ['is_enabled', 'schedule_type', 'get_schedule_description', 'last_run', 'next_run', 'run_now_button']
    fieldsets = (
        ('Основные настройки', {
            'fields': ('is_enabled', 'schedule_type')
        }),
        ('Настройки расписания', {
            'fields': ('custom_hour', 'custom_minute', 'custom_day_of_week', 'custom_day_of_month'),
            'description': 'Настройте время для индексации'
        }),
        ('Информация', {
            'fields': ('last_run', 'next_run'),
            'classes': ('collapse',)
        }),
    )
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('run-now/', self.admin_site.admin_view(self.run_now), name='smbindedschedule_run_now'),
        ]
        return custom_urls + urls
    
    def get_schedule_description(self, obj):
        return str(obj)
    get_schedule_description.short_description = "Расписание"
    
    def run_now_button(self, obj):
        return format_html(
            '<a class="button" href="{}" style="background: #17a2b8;">▶️ Запустить сейчас</a>',
            reverse('admin:smbindedschedule_run_now')
        )
    run_now_button.short_description = "Запуск"
    
    def run_now(self, request):
        """Ручной запуск индексации"""
        if request.method == 'POST':
            task = index_smb_files.delay()
            messages.success(request, f'Индексация запущена (Task ID: {task.id})')
            return HttpResponseRedirect(reverse('admin:statement_smbindexschedule_changelist'))
        
        context = {
            'title': 'Запустить индексацию SMB',
            'opts': self.model._meta,
        }
        return render(request, 'admin/statement/run_index_now.html', context)
    
    def save_model(self, request, obj, form, change):
        """При сохранении обновляем расписание в Celery без использования транзакции"""
        # Сохраняем модель
        super().save_model(request, obj, form, change)
        
        # Обновляем расписание после сохранения, вне транзакции
        # Используем transaction.on_commit для выполнения после фиксации транзакции
        from django.db import transaction as db_transaction
        
        def update_schedule():
            try:
                from statement.scheduler import update_smb_indexing_schedule
                update_smb_indexing_schedule()
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Ошибка при обновлении расписания: {e}")
        
        db_transaction.on_commit(update_schedule)