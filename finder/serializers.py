from rest_framework import serializers
from .models import Remains


class RemainsSerializer(serializers.ModelSerializer):
    status_color = serializers.CharField(read_only=True)  # Аннотированное поле
    price = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    class Meta:
        model = Remains
        fields = '__all__'

class ProjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Remains
        fields = ['id', 'project']


class FileUploadSerializer(serializers.Serializer):
    doc = serializers.FileField()


