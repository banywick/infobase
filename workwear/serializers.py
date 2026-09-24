# backend/workwear/serializers.py

from rest_framework import serializers
from .models import Employee, WorkwearCategory, WorkwearItem, WorkwearHistory
from datetime import timedelta
from django.utils import timezone


class EmployeeSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    # Убираем expiring_count и expired_count, если они не нужны
    # Или оставляем, но с защитой
    expiring_count = serializers.SerializerMethodField()
    expired_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = [
            'id', 'first_name', 'last_name', 'patronymic',
            'department', 'position', 'is_active',
            'full_name', 'expiring_count', 'expired_count',
            'created_at', 'updated_at'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_expiring_count(self, obj):
        """Безопасное получение количества истекающих предметов"""
        if hasattr(obj, 'get_expiring_items'):
            return obj.get_expiring_items().count()
        # Альтернативный способ - напрямую через related_name
        today = timezone.now().date()
        threshold = today + timedelta(days=30)
        return obj.workwear_items.filter(
            expiration_date__gte=today,
            expiration_date__lte=threshold,
            is_active=True
        ).count()
    
    def get_expired_count(self, obj):
        """Безопасное получение количества просроченных предметов"""
        if hasattr(obj, 'get_expired_items'):
            return obj.get_expired_items().count()
        # Альтернативный способ
        today = timezone.now().date()
        return obj.workwear_items.filter(
            expiration_date__lt=today,
            is_active=True
        ).count()


class EmployeeCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            'first_name', 'last_name', 'patronymic',
            'department', 'position', 'is_active'
        ]


class WorkwearCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkwearCategory
        fields = ['id', 'name', 'description', 'standard_lifespan', 'is_active']


class WorkwearItemSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    days_until_expiration = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkwearItem
        fields = [
            'id', 'employee', 'employee_name', 'category', 'category_name',
            'name', 'size', 'color', 'issue_date',
            'expiration_date', 'is_active', 'notes', 'status',
            'days_until_expiration', 'created_at', 'updated_at'
        ]
    
    def get_employee_name(self, obj):
        return obj.employee.get_full_name()
    
    def get_category_name(self, obj):
        return obj.category.name
    
    def get_status(self, obj):
        return obj.get_status()
    
    def get_days_until_expiration(self, obj):
        today = timezone.now().date()
        if obj.expiration_date >= today:
            return (obj.expiration_date - today).days
        return 0


class WorkwearCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkwearItem
        fields = [
            'employee', 'category', 'name', 
            'size', 'color', 'issue_date', 'expiration_date', 
            'is_active', 'notes'
        ]
    
    def create(self, validated_data):
        if 'expiration_date' not in validated_data and 'issue_date' in validated_data:
            category = validated_data.get('category')
            if category:
                issue_date = validated_data.get('issue_date')
                expiration_date = issue_date + timedelta(days=category.standard_lifespan)
                validated_data['expiration_date'] = expiration_date
        
        return super().create(validated_data)


class WorkwearHistorySerializer(serializers.ModelSerializer):
    workwear_item_name = serializers.SerializerMethodField()
    previous_employee_name = serializers.SerializerMethodField()
    new_employee_name = serializers.SerializerMethodField()
    action_display = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkwearHistory
        fields = [
            'id', 'workwear_item', 'workwear_item_name', 'action',
            'action_display', 'previous_employee', 'previous_employee_name',
            'new_employee', 'new_employee_name', 'description',
            'created_at'
        ]
    
    def get_workwear_item_name(self, obj):
        return obj.workwear_item.name
    
    def get_previous_employee_name(self, obj):
        if obj.previous_employee:
            return obj.previous_employee.get_full_name()
        return None
    
    def get_new_employee_name(self, obj):
        if obj.new_employee:
            return obj.new_employee.get_full_name()
        return None
    
    def get_action_display(self, obj):
        return obj.get_action_display()