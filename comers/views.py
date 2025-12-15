from django.views.generic import TemplateView
from rest_framework import generics, status
from rest_framework.views import APIView
from django.db.models import Q
from .serializers import *
from .models import Invoice
from rest_framework.response import Response
from .forms import *
from .utils.filter_session import ComersSessionManager
from common.utils.access_mixin import UserGroupRequiredMixin



class ComersView(UserGroupRequiredMixin,TemplateView):
    """
    Представление для отображения страницы Недопоставок.

    Этот класс наследуется от TemplateView и используется для отображения HTML-шаблона,
    который содержит интерфейс для работы с заметками.

    Attributes:
        template_name (str): Путь к HTML-шаблону, который будет использоваться для отображения страницы.
    """
    template_name = 'comers/index.html'
    group_required = ['sklad', 'comers']

    def get_context_data(self, **kwargs):
        """ Добавляет формы в контекст шаблона."""
        context = super().get_context_data(**kwargs)
        context['input_data_form'] = InputDataForm()
        context['invoice_edit_form'] = InvoiceEditForm()
        context['invoice_edit_form_status'] = InvoiceEditFormStatus()
        context['filter_form'] = FilterForm()
        context['add_suppler_form'] = AddSupplerForm()
        return context


class BaseComersPositionView(generics.GenericAPIView):
    """
    Базовый класс представления для работы с позициями Недопоставок.

    Этот класс наследуется от GenericAPIView и используется для получения и фильтрации
    объектов Invoice на основе параметров, сохраненных в сессии.

    Attributes:
        serializer_class (class): Класс сериализатора для обработки данных Invoice.
        lookup_field (str): Поле, используемое для поиска объектов Invoice.

    Methods:
        get_queryset(): Возвращает отфильтрованный queryset объектов Invoice.
    """
    serializer_class = InvoiceSerializer
    lookup_field = 'id'

    def get_queryset(self):
        """
        Возвращает queryset объектов Invoice, отфильтрованный по параметрам из сессии.

        Returns:
            QuerySet: Отфильтрованный queryset объектов Invoice.
        """
        # Получаем значения из сессии
        leading_id, supplier_id, status_id = ComersSessionManager.get_filter_ids_to_session(self.request)

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
    на получение всех записей. Он использует сериализатор InvoiceSerializer для сериализации данных.

    Attributes:
        queryset (QuerySet): QuerySet, содержащий все объекты модели Invoice.
        serializer_class (Serializer): Сериализатор, используемый для сериализации данных.
    """
    pass


class RemovePosition(BaseComersPositionView, generics.DestroyAPIView):
    """
    Представление для удаления экземпляра а таблице invoice(недопоставки).

    Этот класс наследуется от DestroyAPIView и используется для обработки DELETE-запросов
    на удаление заметок. Он использует сериализатор InvoiceSerializer для валидации данных.

    Attributes:
        queryset (QuerySet): QuerySet, содержащий все объекты модели Comers.
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
    на создание новых заметок. Он использует сериализатор InvoiceSerializer для валидации
    и сохранения данных.

    Attributes:
        queryset (QuerySet): QuerySet, содержащий все объекты модели comers_supler.
        serializer_class (Serializer): Сериализатор, используемый для валидации и сохранения данных.
    """
    queryset = Invoice.objects.all()
    serializer_class = SuplerSerializer


class AddInvoiceData(generics.CreateAPIView):
    """
    Представление для создания экземпляра модели Invoice.

    Этот класс наследуется от CreateAPIView и используется для обработки POST-запросов
    на создание новых записей Invoice. Он использует сериализатор InvoiceSerializerSpecialist
    для валидации и сохранения данных.

    Attributes:
        queryset (QuerySet): QuerySet, содержащий все объекты модели Invoice.
        serializer_class (Serializer): Сериализатор, используемый для валидации и сохранения данных.

    Methods:
        create(request, *args, **kwargs): Обрабатывает POST-запрос для создания новой записи Invoice.
    """
    queryset = Invoice.objects.all()
    serializer_class = InvoiceCreateSerializer


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            # Возвращаем данные через InvoiceSerializer
            instance = serializer.instance
            response_serializer = InvoiceSerializer(instance)
            return Response(
                {
                    "success": True,
                    "data": response_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {"errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    

class RetrieveUpdateInvoiceData(generics.RetrieveUpdateAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceCreateSerializer  # Дефолтный сериализатор
    
    def get_serializer_class(self):
        # Для GET-запросов используем InvoiceSerializer (только чтение)
        # Для PUT/PATCH - InvoiceCreateSerializer (создание/обновление)
        if self.request.method == 'GET':
            return InvoiceSerializer
        return InvoiceCreateSerializer
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # partial=True позволяет частичное обновление (PATCH)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        
        if serializer.is_valid():
            self.perform_update(serializer)
            # После успешного обновления возвращаем данные через InvoiceSerializer
            return Response({
                "success": True,
                "data": InvoiceSerializer(instance).data
            }, status=status.HTTP_200_OK)
        
        return Response(
            {"errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )  

