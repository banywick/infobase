from django.contrib import admin
from .models import Employee, WorkwearCategory, WorkwearItem, WorkwearHistory

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'employee_id', 'department', 'position', 'email', 'is_active']
    list_filter = ['department', 'is_active']
    search_fields = ['user__first_name', 'user__last_name', 'employee_id', 'email']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'ФИО'

@admin.register(WorkwearCategory)
class WorkwearCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'standard_lifespan', 'is_active']
    search_fields = ['name']

@admin.register(WorkwearItem)
class WorkwearItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'employee', 'category', 'issue_date', 'expiration_date', 'get_status']
    list_filter = ['category', 'is_active', 'employee__department']
    search_fields = ['name', 'serial_number', 'employee__user__last_name']
    
    def get_status(self, obj):
        return obj.get_status()
    get_status.short_description = 'Статус'

@admin.register(WorkwearHistory)
class WorkwearHistoryAdmin(admin.ModelAdmin):
    list_display = ['workwear_item', 'action', 'created_at', 'created_by']
    list_filter = ['action']
    search_fields = ['workwear_item__name', 'workwear_item__employee__user__last_name']