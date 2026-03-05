from rest_framework import serializers
from .models import Review, NewsItem


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
        extra_kwargs = {
            'user': {'required': False, 'allow_null': True, 'allow_blank': True}
        }

class NewsItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsItem
        fields = "__all__"