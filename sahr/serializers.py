from rest_framework import serializers
from .models import Data_Table, History
import re

class SahrDataTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Data_Table
        fields = '__all__'

    def validate_address(self, value):
        if re.search(r'[А-Яа-яЁё]', value):
            raise serializers.ValidationError("Адрес должен содержать только латинские буквы и цифры (переключите раскладку).")
        return value


class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = '__all__'        