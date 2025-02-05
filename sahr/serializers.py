from rest_framework import serializers
from .models import Data_Table


class SahrDataTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Data_Table
        fields = '__all__'