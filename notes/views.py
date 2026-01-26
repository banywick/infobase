from django.views.generic import TemplateView
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Note
from .serializers import NoteSerializer
from common.utils.access_mixin import UserGroupRequiredMixin
from django.utils import timezone
import json
from rest_framework.permissions import IsAuthenticated

class NotesView(UserGroupRequiredMixin, TemplateView):
    """Представление для страницы заметок"""
    template_name = 'notes/index.html'
    group_required = ['sklad']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.request.user.username
        return context

class BaseNoteView(generics.GenericAPIView):
    """Базовый класс для заметок"""
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    # permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Пользователь видит только свои заметки
        return Note.objects.filter(user=self.request.user).order_by('-id')

class AddNoteView(generics.CreateAPIView):
    """Создание заметки"""
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        print(f"=== СОЗДАНИЕ ЗАМЕТКИ ===")
        print(f"Пользователь: {request.user.username}")
        print(f"Текст заметки: {request.data.get('text', '')[:100]}...")
        
        try:
            # Получаем текст из запроса
            text = request.data.get('text', '').strip()
            
            if not text:
                return Response(
                    {'detail': 'Текст заметки не может быть пустым'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Создаем заметку для текущего пользователя
            # Модель Note имеет только поля user и text
            note = Note.objects.create(
                user=request.user,
                text=text
            )
            
            print(f"Заметка создана: ID={note.id}")
            
            # Сериализуем и возвращаем ответ
            serializer = self.get_serializer(note)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"Ошибка: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return Response(
                {'detail': f'Ошибка сервера: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class GetAllNotes(BaseNoteView, generics.ListAPIView):
    """Получение всех заметок пользователя"""
    pass

class EditNote(BaseNoteView, generics.RetrieveUpdateAPIView):
    """Редактирование заметки"""
    lookup_field = 'id'
    
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

class RemoveNote(BaseNoteView, generics.DestroyAPIView):
    """Удаление заметки"""
    lookup_field = 'id'
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {'message': 'Заметка успешно удалена'},
            status=status.HTTP_200_OK
        )