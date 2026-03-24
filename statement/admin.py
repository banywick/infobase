# admin.py

from django.contrib import admin
from .models import SMBPathConfig

@admin.register(SMBPathConfig)
class SMBPathConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'search_path', 'result_path', 'is_active', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'search_path', 'result_path', 'description']
    list_editable = ['is_active']
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('SMB пути', {
            'fields': ('search_path', 'result_path'),
            'description': 'Укажите полные пути к SMB папкам'
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']