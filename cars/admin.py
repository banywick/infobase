from django.contrib import admin
from finder.models import Remains
from .models import InventoryItem



@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ['number', 'article', 'name', 'quantity', 'arrival_date']
    list_filter = ['arrival_date']
    search_fields = ['number', 'article', 'name']