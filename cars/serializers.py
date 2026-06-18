# cars/serializers.py
from rest_framework import serializers
from .models import Location, InventoryItem


class LocationSerializer(serializers.ModelSerializer):
    """Сериализатор для мест хранения"""
    
    class Meta:
        model = Location
        fields = ['id', 'name', 'code', 'is_active']
        read_only_fields = ['id']


class InventoryItemSerializer(serializers.ModelSerializer):
    """Сериализатор для инвентарных записей"""
    
    location_name = serializers.CharField(source='location.name', read_only=True)
    location_id = serializers.IntegerField(source='location.id', read_only=True)
    children_count = serializers.IntegerField(read_only=True)
    has_children = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = InventoryItem
        fields = [
            'id', 'number', 'arrival_date', 'article', 'name',
            'location', 'location_name', 'location_id',
            'quantity', 'comment', 'parent',
            'children_count', 'has_children',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']