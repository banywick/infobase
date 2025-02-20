from django.contrib import admin
from .models import UniqueIP, RequestCounter

@admin.register(UniqueIP)
class UniqueIPAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'first_request_time', 'name')
    search_fields = ('ip_address', 'name')

@admin.register(RequestCounter)
class RequestCounterAdmin(admin.ModelAdmin):
    list_display = ('count',)
