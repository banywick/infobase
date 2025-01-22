from rest_framework import serializers
from .models import Remains

class RemainsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Remains()
        exclude = ['price']


class ProjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Remains()
        fields = ['id', 'project']