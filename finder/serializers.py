from rest_framework import serializers
from .models import Remains

class RemainsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Remains()
        fields = '__all__'
        # fields = ['article']
