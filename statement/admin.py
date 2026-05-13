# statement/admin.py

from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect, render
from django.utils.html import format_html
from django.urls import reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.utils import timezone
from django.contrib import messages
from .models import SMBPathConfig, SMBFileIndex, ProcessedFileLog
from .tasks import index_search_files, populate_accounting_data
from celery.result import AsyncResult


@admin.register(SMBPathConfig)
class SMBPathConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'config_type', 'search_path', 'is_active', 'index_status', 'action_buttons']
    list_filter = ['config_type', 'is_active']
    search_fields = ['name', 'description']
    
    fieldsets = (
        ('Основные настройки', {
            'fields': ('name', 'config_type', 'description', 'is_active')
        }),
        ('Пути для SMB', {
            'fields': ('search_path', 'result_path'),
            'description': 'Укажите пути к SMB ресурсам'
        }),
    )
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('reindex/<int:config_id>/', self.admin_site.admin_view(self.reindex_single), name='smbpathconfig_reindex_single'),
            path('populate/<int:config_id>/', self.admin_site.admin_view(self.populate_accounting), name='populate_accounting_data'),
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
    
    def action_buttons(self, obj):
        buttons = []
        
        # Кнопка индексации (для всех типов)
        buttons.append(f'<a class="button" href="{reverse("admin:smbpathconfig_reindex_single", args=[obj.id])}">🔄 Индексировать</a>')
        
        # Кнопка обработки только для accounting_source
        if obj.config_type == 'accounting_source':
            buttons.append(f'<a class="button" href="{reverse("admin:populate_accounting_data", args=[obj.id])}" style="background: #28a745;">📥 В AccountingData</a>')
        
        return format_html(' '.join(buttons))
    action_buttons.short_description = "Действия"
    
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
    
    def populate_accounting(self, request, config_id):
        """Запуск populate AccountingData для конфигурации"""
        if request.method == 'POST':
            task = populate_accounting_data.delay(config_id=config_id)
            messages.success(request, f'Задача запущена. ID: {task.id}')
            return HttpResponseRedirect(reverse('admin:statement_smbpathconfig_changelist'))
        
        config = SMBPathConfig.objects.get(id=config_id)
        context = {
            'title': f'Пополнение AccountingData из {config.name}',
            'config': config,
            'opts': self.model._meta,
        }
        return render(request, 'admin/statement/populate_accounting_confirmation.html', context)
    
    def check_task_status(self, request, task_id):
        """Проверка статуса задачи"""
        task = AsyncResult(task_id)
        result = {
            'task_id': task_id,
            'status': task.status,
            'ready': task.ready(),
            'result': task.result if task.ready() else None
        }
        return JsonResponse(result)


@admin.register(SMBFileIndex)
class SMBFileIndexAdmin(admin.ModelAdmin):
    list_display = ['filename', 'config', 'processing_status', 'is_available', 'processed_at']
    list_filter = ['config', 'processing_status', 'is_available', 'file_extension']
    search_fields = ['filename', 'relative_path', 'file_path', 'processing_error']
    readonly_fields = ['file_path', 'relative_path', 'file_size', 'modified_time', 'created_at']
    actions = ['mark_as_pending', 'mark_as_processed', 'reprocess_selected']
    
    fieldsets = (
        ('Информация о файле', {
            'fields': ('filename', 'config', 'file_extension', 'file_path', 'relative_path')
        }),
        ('Статус обработки', {
            'fields': ('processing_status', 'processed_at', 'processing_error')
        }),
        ('Техническая информация', {
            'fields': ('file_size', 'modified_time', 'is_available', 'last_checked', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def mark_as_pending(self, request, queryset):
        count = queryset.update(processing_status='pending', processed_at=None, processing_error='')
        self.message_user(request, f"{count} файлов отмечены для повторной обработки")
    mark_as_pending.short_description = "Отметить для повторной обработки"
    
    def mark_as_processed(self, request, queryset):
        count = queryset.update(processing_status='processed', processed_at=timezone.now())
        self.message_user(request, f"{count} файлов отмечены как обработанные")
    mark_as_processed.short_description = "Отметить как обработанные"
    
    def reprocess_selected(self, request, queryset):
        from .tasks import process_smb_files
        for file_index in queryset:
            file_index.processing_status = 'pending'
            file_index.save()
        self.message_user(request, f"Запущена обработка для {queryset.count()} файлов")
    reprocess_selected.short_description = "Переобработать выбранные"


@admin.register(ProcessedFileLog)
class ProcessedFileLogAdmin(admin.ModelAdmin):
    list_display = ['file_index', 'processed_at', 'rows_processed', 'status']
    list_filter = ['status', 'processed_at']
    search_fields = ['file_index__filename', 'error_message']
    readonly_fields = ['file_index', 'processed_at', 'rows_processed', 'status', 'error_message']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False