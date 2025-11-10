from django.shortcuts import render
from rest_framework import generics, permissions
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response

class LoginView(generics.GenericAPIView):
    """Авторизация"""
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        print(request.data)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response(UserSerializer(user).data)
        else:
            return Response({"error": "Неверный логин или пароль"}, status=400)
        

class RegisterView(generics.CreateAPIView):
    """Регистрация"""
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer
        

class LogoutView(APIView):
    """Выход из системы"""
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        logout(request)
        return Response({"detail": "Successfully logged out."})
