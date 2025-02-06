from rest_framework import serializers
from .models import Data_Table, History


class SahrDataTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Data_Table
        fields = '__all__'


class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = '__all__'        