from rest_framework import serializers
from .models import Remains


class RemainsSerializer(serializers.ModelSerializer):
    status_color = serializers.CharField(read_only=True)
    price = serializers.CharField(read_only=True)  # Просто как строка
    
    class Meta:
        model = Remains
        fields = '__all__'

class ProjectListSerializer(serializers.ModelSerializer):
    status_color = serializers.CharField(read_only=True)
    class Meta:
        model = Remains
        fields = ['id', 'project', 'status_color']


class FileUploadSerializer(serializers.Serializer):
    doc = serializers.FileField()


