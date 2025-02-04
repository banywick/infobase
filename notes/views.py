from django.views.generic import TemplateView
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Note
from .serializers import NoteSerializer

class NotesView(TemplateView):
    """
    Представление для отображения страницы заметок.

    Этот класс наследуется от TemplateView и используется для отображения HTML-шаблона,
    который содержит интерфейс для работы с заметками.

    Attributes:
        template_name (str): Путь к HTML-шаблону, который будет использоваться для отображения страницы.
    """
    template_name = 'notes/index.html'

class AddNoteView(generics.CreateAPIView):
    """
    Представление для создания новой заметки.

    Этот класс наследуется от CreateAPIView и используется для обработки POST-запросов
    на создание новых заметок. Он использует сериализатор NoteSerializer для валидации
    и сохранения данных.

    Attributes:
        queryset (QuerySet): QuerySet, содержащий все объекты модели Note.
        serializer_class (Serializer): Сериализатор, используемый для валидации и сохранения данных.
    """
    queryset = Note.objects.all()
    serializer_class = NoteSerializer

class RemoveNote(generics.DestroyAPIView):
    """
    Представление для удаления заметки.

    Этот класс наследуется от DestroyAPIView и используется для обработки DELETE-запросов
    на удаление заметок. Он использует сериализатор NoteSerializer для валидации данных.

    Attributes:
        queryset (QuerySet): QuerySet, содержащий все объекты модели Note.
        serializer_class (Serializer): Сериализатор, используемый для валидации данных.
        lookup_field (str): Поле, используемое для поиска объекта.

    Methods:
        destroy(request, *args, **kwargs): Удаляет объект и возвращает ответ с сообщением об успешном удалении.
    """
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        """
        Удаляет объект и возвращает ответ с сообщением об успешном удалении.

        Args:
            request (Request): Объект запроса.
            *args: Дополнительные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Returns:
            Response: Ответ с сообщением об успешном удалении.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'successfully deleted'}, status=status.HTTP_200_OK)

class GetAllNotes(generics.ListAPIView):
    """
    Представление для получения всех заметок.

    Этот класс наследуется от ListAPIView и используется для обработки GET-запросов
    на получение всех заметок. Он использует сериализатор NoteSerializer для сериализации данных.

    Attributes:
        queryset (QuerySet): QuerySet, содержащий все объекты модели Note.
        serializer_class (Serializer): Сериализатор, используемый для сериализации данных.
    """
    queryset = Note.objects.all()
    serializer_class = NoteSerializer

class EditNote(generics.UpdateAPIView):
    """
    Представление для редактирования заметки.

    Этот класс наследуется от UpdateAPIView и используется для обработки PUT- и PATCH-запросов
    на редактирование заметок. Он использует сериализатор NoteSerializer для валидации и сохранения данных.

    Attributes:
        queryset (QuerySet): QuerySet, содержащий все объекты модели Note.
        serializer_class (Serializer): Сериализатор, используемый для валидации и сохранения данных.
        lookup_field (str): Поле, используемое для поиска объекта.

    Methods:
        update(request, *args, **kwargs): Обновляет объект и возвращает ответ с обновленными данными.
    """
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        """
        Обновляет объект и возвращает ответ с обновленными данными.

        Args:
            request (Request): Объект запроса.
            *args: Дополнительные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Returns:
            Response: Ответ с обновленными данными.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
