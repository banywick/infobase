from django.views.generic import TemplateView
from rest_framework import generics, status
from rest_framework.views import APIView
from django.db.models import Q
from .serializers import *
from .models import Invoice
from rest_framework.response import Response
from .forms import *
from .utils.filter_session import ComersSessionManager

class ComersView(TemplateView):
    """
    Представление для отображения страницы Недопоставок.

    Этот класс наследуется от TemplateView и используется для отображения HTML-шаблона,
    который содержит интерфейс для работы с заметками.

    Attributes:
        template_name (str): Путь к HTML-шаблону, который будет использоваться для отображения страницы.
    """
    template_name = 'comers/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['input_data_form'] = InputDataForm()
        context['invoice_edit_form'] = InvoiceEditForm()
        context['invoice_edit_form_status'] = InvoiceEditFormStatus()
        context['filter_form'] = FilterForm()
        context['add_suppler_form'] = AddSupplerForm()
        return context

    


class BaseComersPositionView(generics.GenericAPIView):
    serializer_class = InvoiceSerializer
    lookup_field = 'id'

    def get_queryset(self):
        # Получаем значения из сессии
        leading_id, supplier_id, status_id = ComersSessionManager.get_filter_ids_to_session(self.request)
        filter_names = ComersSessionManager.get_filter_name_field(self.request)
        print(filter_names)

        # Создаем Q-объекты для фильтрации только если значения не пустые
        filters = Q()

        if leading_id:
            filters &= Q(leading_id=leading_id)
        if supplier_id:
            filters &= Q(supplier_id=supplier_id)
        if status_id:
            filters &= Q(status_id=status_id)

        # Применяем фильтры к queryset
        return Invoice.objects.filter(filters)


class GetAllPositions(BaseComersPositionView, generics.ListAPIView):
    """
    Представление для получения всех сущностей таблицы Invoce(commers/недопоставки).

    Этот класс наследуется от ListAPIView и используется для обработки GET-запросов
    на получение всех заметок. Он использует сериализатор NoteSerializer для сериализации данных.

    Attributes:
        queryset (QuerySet): QuerySet, содержащий все объекты модели Note.
        serializer_class (Serializer): Сериализатор, используемый для сериализации данных.
    """
    pass


class RemovePosition(BaseComersPositionView, generics.DestroyAPIView):
    """
    Представление для удаления экземпляра а таблице comers(недопоставки).

    Этот класс наследуется от DestroyAPIView и используется для обработки DELETE-запросов
    на удаление заметок. Он использует сериализатор InvoiceSerializer для валидации данных.

    Attributes:
        queryset (QuerySet): QuerySet, содержащий все объекты модели Note.
        serializer_class (Serializer): Сериализатор, используемый для валидации данных.
        lookup_field (str): Поле, используемое для поиска объекта.

    Methods:
        destroy(request, *args, **kwargs): Удаляет объект и возвращает ответ с сообщением об успешном удалении.
    """

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
    

class AddSupplier(generics.CreateAPIView): 
    """
    Представление для создания нового поставщика в таблице "comers_supler".

    Этот класс наследуется от CreateAPIView и используется для обработки POST-запросов
    на создание новых заметок. Он использует сериализатор NoteSerializer для валидации
    и сохранения данных.

    Attributes:
        queryset (QuerySet): QuerySet, содержащий все объекты модели Note.
        serializer_class (Serializer): Сериализатор, используемый для валидации и сохранения данных.
    """
    queryset = Invoice.objects.all()
    serializer_class = SuplerSerializer


class AddInvoiceData(generics.CreateAPIView):
    """
    Представление для создания ......

    Этот класс наследуется от CreateAPIView и используется для обработки POST-запросов
    на создание новых заметок. Он использует сериализатор NoteSerializer для валидации
    и сохранения данных.

    Attributes:
        queryset (QuerySet): QuerySet, содержащий все объекты модели Note.
        serializer_class (Serializer): Сериализатор, используемый для валидации и сохранения данных.
    """
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializerSpecialist


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({"success": True}, status=status.HTTP_200_OK)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

class AddFilterInvoiceData(APIView):
    def post(self, request):
        # Извлекаем значения из данных запроса
        supplier_id = request.data.get('supplier')
        leading_id = request.data.get('leading')
        status_id = request.data.get('status')

        request.session['supplier_id'] = supplier_id
        request.session['leading_id'] = leading_id
        request.session['status_id'] = status_id

        # Возвращаем ответ
        return Response({"message": "Filter values saved successfully."}, status=status.HTTP_200_OK)
    

class GetFilterInvoiceData(APIView):
    def get(self, request):
        filter_names = ComersSessionManager.get_filter_name_field(request)
        return Response(filter_names, status=status.HTTP_200_OK)
    

class ClearFilterInvoiceData(APIView):
    def post(self, reqyest):
        if 'leading_id' in self.request.session:
            del self.request.session['leading_id']
        if 'supplier_id' in self.request.session:
            del self.request.session['supplier_id']
        if 'status_id' in self.request.session:
            del self.request.session['status_id']

        return Response({"message": "clear successfully"}, status=status.HTTP_200_OK)



