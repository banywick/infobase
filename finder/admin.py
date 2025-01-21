from django.contrib import admin
from .models import Standard, Metiz

class StandardAdmin(admin.ModelAdmin):
    list_display = ('number', 'type_standarts')
    search_fields = ('number', 'type_standarts')
    list_filter = ('type_standarts',)

class MetizAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_gost', 'display_din', 'display_iso')
    search_fields = ('name',)
    filter_horizontal = ('standards',)

    def display_gost(self, obj):
        return ", ".join([standard.number for standard in obj.standards.filter(type_standarts='GOST')])
    display_gost.short_description = 'GOST'

    def display_din(self, obj):
        return ", ".join([standard.number for standard in obj.standards.filter(type_standarts='DIN')])
    display_din.short_description = 'DIN'

    def display_iso(self, obj):
        return ", ".join([standard.number for standard in obj.standards.filter(type_standarts='ISO')])
    display_iso.short_description = 'ISO'

admin.site.register(Standard, StandardAdmin)
admin.site.register(Metiz, MetizAdmin)
