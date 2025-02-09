from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework import generics, status
from .serializers import InvoiceSerializer
from .models import Invoice

class ComersView(TemplateView):
    """
    Представление для отображения страницы Недопоставок.

    Этот класс наследуется от TemplateView и используется для отображения HTML-шаблона,
    который содержит интерфейс для работы с заметками.

    Attributes:
        template_name (str): Путь к HTML-шаблону, который будет использоваться для отображения страницы.
    """
    template_name = 'comers/index.html'


class BaseComersPositionView(generics.GenericAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    lookup_field = 'id'

class AllPositionsView(BaseComersPositionView, generics.ListAPIView):
    """
    Представление для получения всех сущностей таблицы Invoce(commers/недопоставки).

    Этот класс наследуется от ListAPIView и используется для обработки GET-запросов
    на получение всех заметок. Он использует сериализатор NoteSerializer для сериализации данных.

    Attributes:
        queryset (QuerySet): QuerySet, содержащий все объекты модели Note.
        serializer_class (Serializer): Сериализатор, используемый для сериализации данных.
    """
    pass
