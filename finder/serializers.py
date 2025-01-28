from rest_framework import serializers
from .models import Remains
from django.contrib.auth.models import User

class RemainsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Remains()
        exclude = ['price']


class ProjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Remains()
        fields = ['id', 'project']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password')

class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True},
            'password2': {'write_only': True}
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Пароли не совпадают!.")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')  # Удаляем password2 перед созданием пользователя
        user = User.objects.create_user(
            username=validated_data['username'],
            email='',  # Передаем пустую строку для email
            password=validated_data['password']
        )
        return user