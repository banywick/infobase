# statement/admin.py
from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect, render
from django.contrib import messages
from django.utils.html import format_html
from django.urls import reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.db import transaction
from .models import SMBPathConfig, SMBFileIndex
from .tasks import index_smb_files
from celery.result import AsyncResult
import json


@admin.register(SMBPathConfig)
class SMBPathConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'search_path', 'result_path', 'is_active', 'index_status']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    actions = ['reindex_selected']
    
    
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
    


@admin.register(SMBFileIndex)
class SMBFileIndexAdmin(admin.ModelAdmin):
    list_display = ['filename', 'config', 'file_extension', 'is_available', 'last_checked']
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

