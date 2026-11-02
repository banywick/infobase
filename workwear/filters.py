from django_filters import rest_framework as filters
from .models import Employee, WorkwearItem
from django.db.models import Q

class EmployeeFilter(filters.FilterSet):
    """Фильтр для сотрудников"""
    search = filters.CharFilter(method='filter_search', label='Поиск')
    department = filters.CharFilter(lookup_expr='icontains', label='Отдел')
    is_active = filters.BooleanFilter(label='Активен')
    
    class Meta:
        model = Employee
        fields = {
            'department': ['icontains'],
            'is_active': ['exact'],
        }
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(user__first_name__icontains=value) |
            Q(user__last_name__icontains=value) |
            Q(user__username__icontains=value) |
            Q(employee_id__icontains=value) |
            Q(department__icontains=value)
        )

class WorkwearItemFilter(filters.FilterSet):
    """Фильтр для предметов спецодежды"""
    search = filters.CharFilter(method='filter_search', label='Поиск')
    expiration_from = filters.DateFilter(field_name='expiration_date', lookup_expr='gte', label='Срок истечения с')
    expiration_to = filters.DateFilter(field_name='expiration_date', lookup_expr='lte', label='Срок истечения по')
    status = filters.CharFilter(method='filter_status', label='Статус')
    employee_id = filters.NumberFilter(field_name='employee__id', label='ID сотрудника')
    category_id = filters.NumberFilter(field_name='category__id', label='ID категории')
    
    class Meta:
        model = WorkwearItem
        fields = {
            'employee__id': ['exact'],
            'category__id': ['exact'],
            'expiration_date': ['gte', 'lte'],
        }
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(serial_number__icontains=value) |
            Q(employee__user__first_name__icontains=value) |
            Q(employee__user__last_name__icontains=value) |
            Q(category__name__icontains=value)
        )
    
    def filter_status(self, queryset, name, value):
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        
        if value == 'expired':
            return queryset.filter(expiration_date__lt=today, is_active=True)
        elif value == 'expiring_soon':
            threshold = today + timedelta(days=30)
            return queryset.filter(expiration_date__gte=today, expiration_date__lte=threshold, is_active=True)
        elif value == 'active':
            return queryset.filter(expiration_date__gt=today, is_active=True)
        return queryset