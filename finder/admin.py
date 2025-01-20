from django.contrib import admin
from .models import Standard, Item

class StandardAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

class ItemAdmin(admin.ModelAdmin):
    list_display = ('type',)
    list_filter = ('type',)
    search_fields = ('type',)

admin.site.register(Standard, StandardAdmin)
admin.site.register(Item, ItemAdmin)