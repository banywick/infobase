from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User.

    Этот сериализатор используется для представления пользователя с полями 'id', 'username' и 'password'.

    Attributes:
        Meta: Внутренний класс для настройки сериализатора.
            model (User): Модель, для которой предназначен сериализатор.
            fields (tuple): Поля, которые будут сериализованы.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'password')

class RegisterSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации нового пользователя.

    Этот сериализатор используется для создания нового пользователя с полями 'id', 'username', 'password' и 'password2'.
    Поле 'password2' используется для подтверждения пароля.

    Attributes:
        password2 (CharField): Поле для подтверждения пароля.
        Meta: Внутренний класс для настройки сериализатора.
            model (User): Модель, для которой предназначен сериализатор.
            fields (list): Поля, которые будут сериализованы.
            extra_kwargs (dict): Дополнительные параметры для полей.

    Methods:
        validate(data): Метод для валидации данных. Проверяет, что пароли совпадают.
        create(validated_data): Метод для создания нового пользователя. Удаляет поле 'password2' перед созданием пользователя.
    """
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True},
            'password2': {'write_only': True}
        }

    def validate(self, data):
        """
        Валидация данных.

        Проверяет, что пароли совпадают.

        Args:
            data (dict): Данные для валидации.

        Raises:
            serializers.ValidationError: Если пароли не совпадают.

        Returns:
            dict: Валидированные данные.
        """
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Пароли не совпадают!.")
        return data

    def create(self, validated_data):
        """
        Создание нового пользователя.

        Удаляет поле 'password2' перед созданием пользователя.

        Args:
            validated_data (dict): Валидированные данные.

        Returns:
            User: Созданный пользователь.
        """
        validated_data.pop('password2')  # Удаляем password2 перед созданием пользователя
        user = User.objects.create_user(
            username=validated_data['username'],
            email='',  # Передаем пустую строку для email
            password=validated_data['password']
        )
        return user