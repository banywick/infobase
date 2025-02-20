from django.contrib import admin
from .models import *

@admin.register(Data_Table)
class DataTableAdmin(admin.ModelAdmin):
    list_display = ('article', 'party', 'title', 'comment', 'date', 'address')
    search_fields = ('article', 'title', 'address')
    list_filter = ('date',)
    list_per_page = 100  # Установите количество строк на странице

@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ('article', 'party', 'title', 'comment', 'date', 'address')
    search_fields = ('article', 'title')
    list_filter = ('date',)
    list_per_page = 100

@admin.register(Deleted)
class DeletedAdmin(admin.ModelAdmin):
    list_display = ('article', 'party', 'title', 'date', 'address')
    search_fields = ('article', 'title')
    list_filter = ('date',)
    list_per_page = 100
