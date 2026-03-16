from rest_framework import serializers
from .models import AccountingData, Remains


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



class AccountingDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountingData
        fields = ['accounting_code', 'nomenclature_kd', 'accounting_name']



