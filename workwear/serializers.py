from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Employee, WorkwearCategory, WorkwearItem, WorkwearHistory
from datetime import datetime, timedelta
from django.utils import timezone

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    expiring_count = serializers.SerializerMethodField()
    expired_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = [
            'id', 'user', 'employee_id', 'department', 'position', 
            'phone', 'email', 'photo', 'ldap_dn', 'is_active',
            'full_name', 'expiring_count', 'expired_count',
            'created_at', 'updated_at'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_expiring_count(self, obj):
        return obj.get_expiring_items().count()
    
    def get_expired_count(self, obj):
        return obj.get_expired_items().count()

class EmployeeCreateUpdateSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True, required=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'user_id', 'employee_id', 'department', 'position', 
            'phone', 'email', 'photo', 'ldap_dn', 'is_active'
        ]
    
    def create(self, validated_data):
        user_id = validated_data.pop('user_id')
        user = User.objects.get(id=user_id)
        employee = Employee.objects.create(user=user, **validated_data)
        return employee
    
    def update(self, instance, validated_data):
        if 'user_id' in validated_data:
            user_id = validated_data.pop('user_id')
            user = User.objects.get(id=user_id)
            instance.user = user
        return super().update(instance, validated_data)

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
            'name', 'serial_number', 'size', 'color', 'issue_date',
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
            'employee', 'category', 'name', 'serial_number', 
            'size', 'color', 'issue_date', 'expiration_date', 
            'is_active', 'notes'
        ]
    
    def create(self, validated_data):
        # Автоматически вычисляем дату истечения срока если не указана
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
    created_by_name = serializers.SerializerMethodField()
    action_display = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkwearHistory
        fields = [
            'id', 'workwear_item', 'workwear_item_name', 'action',
            'action_display', 'previous_employee', 'previous_employee_name',
            'new_employee', 'new_employee_name', 'description',
            'created_at', 'created_by', 'created_by_name'
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
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None
    
    def get_action_display(self, obj):
        return dict(self.ACTION_CHOICES).get(obj.action, obj.action)