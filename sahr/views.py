from django.db.models import Q, Sum, OuterRef, Exists, Case, When, Value, IntegerField
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView
from django.views.generic import TemplateView
from rest_framework import generics, status
from finder.models import Remains
from .utils.article_utils import check_article
from .serializers import HistorySerializer, SahrDataTableSerializer
from .models import *
from rest_framework.response import Response



class BasePositionView(generics.GenericAPIView):
    """
    Базовое представление для работы с позициями.

    Этот класс предоставляет базовую функциональность для работы с позициями,
    определяя набор данных и сериализатор, которые будут использоваться
    в производных представлениях.

    Атрибуты:
        queryset (QuerySet): Набор данных, содержащий все объекты Data_Table.
        serializer_class (Serializer): Класс сериализатора для обработки данных.
        lookup_field (str): Поле, используемое для поиска конкретного объекта.

    """
    queryset = Data_Table.objects.all()
    serializer_class = SahrDataTableSerializer
    lookup_field = 'id'

class SahrView(TemplateView):
    """Главная страница САХР"""

    template_name = 'sahr/index.html'

    def get_context_data(self):
        """Меняем в (адресном хранении) Data Table
        статус в столбце index_remains. 0 отсуствует в осномной базе, 
        1 присутсвует в основной базе
        Проеряется каждый раз при перезагрузке страницы
        """
        # Подзапрос для проверки существования артикула в Remains
        remains_subquery = Remains.objects.filter(article=OuterRef('article'))

        # Обновляем Data_Table с использованием Case и When
        Data_Table.objects.update(
            index_remains=Case(
                When(Exists(remains_subquery), then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            )
        )


class SahrArchiveView(TemplateView):
    """Страница с архивом"""
    template_name = 'sahr/archive.html'

class AllArchiveRemovePosition(generics.ListAPIView):
    """
    Представление для отображения всех удаленных позиций.

    Этот класс наследуется от ListAPIView и предоставляет функциональность для
    отображения списка всех позиций, которые были удалены и сохранены в архиве.

    Атрибуты:
        queryset (QuerySet): Набор данных, содержащий все объекты Deleted,
                            представляющие удаленные позиции.
        serializer_class (Serializer): Класс сериализатора для обработки данных

    """

    queryset = Deleted.objects.all()
    serializer_class = SahrDataTableSerializer


class SahrFindFilterArchive(APIView):
    """
    Представление для поиска в архиве удаленных позиций.

    Этот класс предоставляет функциональность для выполнения поиска по архиву
    удаленных позиций на основе запроса, переданного в теле POST-запроса.
    Поиск осуществляется по нескольким полям: article, party и address.


    Методы:
        post(request, *args, **kwargs):
            Обрабатывает POST-запрос для выполнения поиска в архиве.

    """
    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запрос для выполнения поиска в архиве.

        Этот метод извлекает строку запроса из данных запроса, создает Q-объекты
        для каждого из полей (article, party, address), объединяет их с помощью
        логического "или" и фильтрует данные в таблице Deleted. Возвращает
        результаты в формате JSON.

        Аргументы:
            request (HttpRequest): Объект HTTP-запроса.
            *args: Дополнительные позиционные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Возвращает:
            Response: JSON-ответ, содержащий результаты поиска.

        """
        query = request.data.get('query', '')

        # Создаем Q-объекты для каждого поля
        article = Q(article__icontains=query)
        party = Q(party__icontains=query)
        address = Q(address__icontains=query)

        # Объединяем Q-объекты с помощью логического "или"
        combined_query = article | party | address

        # Фильтруем данные в таблице
        results = Deleted.objects.filter(combined_query)

        # Возвращаем результаты в формате JSON
        return Response(results.values())


class SahrFindFilter(APIView):
    """
    Представление для поиска позиций в основной таблице данных САХР

    Этот класс предоставляет функциональность для выполнения поиска по основной
    таблице данных на основе запроса, переданного в теле POST-запроса. Поиск
    осуществляется по нескольким полям: article, party и address.

    Методы:
        post(request, *args, **kwargs):
            Обрабатывает POST-запрос для выполнения поиска в основной таблице данных.

    """
    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запрос для выполнения поиска в основной таблице данных.

        Этот метод извлекает строку запроса из данных запроса, создает Q-объекты
        для каждого из полей (article, party, address), объединяет их с помощью
        логического "или" и фильтрует данные в таблице Data_Table. Возвращает
        результаты в формате JSON.

        Аргументы:
            request (HttpRequest): Объект HTTP-запроса.
            *args: Дополнительные позиционные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Возвращает:
            Response: JSON-ответ, содержащий результаты поиска.

        """
        query = request.data.get('query', '')

        # Создаем Q-объекты для каждого поля
        article = Q(article__icontains=query)
        party = Q(party__icontains=query)
        address = Q(address__icontains=query)

        # Объединяем Q-объекты с помощью логического "или"
        combined_query = article | party | address

        # Фильтруем данные в таблице
        results = Data_Table.objects.filter(combined_query)

        # Возвращаем результаты в формате JSON
        return Response(results.values())
    
    
    
class GetSahrAllPositions(BasePositionView, generics.ListAPIView):
    """
    Представление для получения всех позиций из таблицы САХР.

    Этот класс наследуется от BasePositionView и ListAPIView, чтобы предоставить
    функциональность для отображения списка всех позиций, содержащихся в таблице
    САХР. Он использует набор данных и сериализатор, определенные в BasePositionView.

    Атрибуты:
        Нет (используются атрибуты, определенные в BasePositionView)

    Методы:
        Нет (используются методы, предоставляемые ListAPIView)

    """
    pass



class AddPositions(BasePositionView, CreateAPIView):
    """
    Класс для добавления позиций в Data_Table.

    Этот класс наследует от BasePositionView и CreateAPIView.
    Он обрабатывает POST-запросы для создания новых позиций в Data_Table.
    """

    def create(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запрос для создания новой позиции в Data_Table.

        Args:
            request: HTTP-запрос.

        Returns:
            Response: HTTP-ответ с результатом операции.
        """
        # Создаем изменяемую копию request.data
        data = request.data.copy()

        # Получаем нужные данные с request.data
        instance_id = data.get('id')
        instance_address = data.get('address')
        instance_party = data.get('party')

        try:
            # Находим экземпляр модели Remains по id
            instance = Remains.objects.get(id=instance_id)

            # Получаем артикул из найденного экземпляра
            article = instance.article

            # Заменяем артикул в передаваемых данных
            data['article'] = article

            # Нельзя несколько одинаковых партий сохранять на одном адресе
            part_address = Data_Table.objects.filter(Q(party=instance_party) & Q(address=instance_address))
            if part_address.exists():
                return Response({"error": "Такая позиция уже существует"}, status=status.HTTP_409_CONFLICT)

            # Используем ваш сериализатор для обработки данных
            serializer = SahrDataTableSerializer(data=data)
            serializer.is_valid(raise_exception=True)  # Проверяем валидность данных

            # Сохраняем данные
            serializer.save()

            # Получаем количество записей в Data_Table
            count_row = Data_Table.objects.all().count()

            # Возвращаем ответ
            return Response({"data": serializer.data, "count_row": count_row}, status=status.HTTP_201_CREATED)

        except Remains.DoesNotExist:
            # Если экземпляр Remains не найден, возвращаем ошибку
            return Response({"error": "Remains instance not found"}, status=status.HTTP_404_NOT_FOUND)


class EditPosition(BasePositionView, generics.RetrieveUpdateAPIView):
    """
    Представление для получения и обновления информации о позиции.

    Этот класс наследуется от BasePositionView и RetrieveUpdateAPIView, чтобы
    предоставить функциональность для получения и обновления информации о
    конкретной позиции.


    Методы:
        Нет (используются методы, предоставляемые RetrieveUpdateAPIView)

    """
    pass
    
    
class RemovePosition(BasePositionView, DestroyAPIView):
    """
    Представление для удаления конкретного экземпляра позиции.

    Этот класс наследуется от BasePositionView и DestroyAPIView, чтобы предоставить
    функциональность для удаления экземпляра позиции. Он переопределяет метод destroy,
    чтобы настроить сообщение ответа при успешном удалении.


    Методы:
        destroy(request, *args, **kwargs):
            Удаляет указанный экземпляр позиции и возвращает сообщение об успехе.

    """

    def destroy(self, request, *args, **kwargs):
        """
        Удаляет указанный экземпляр позиции.

        Этот метод извлекает экземпляр позиции для удаления с помощью метода
        `get_object`, выполняет удаление с помощью `perform_destroy` и возвращает
        JSON-ответ с сообщением об успехе.

        Аргументы:
            request (HttpRequest): Объект HTTP-запроса.
            *args: Дополнительные позиционные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Возвращает:
            Response: JSON-ответ с сообщением об успехе и HTTP-статусом 200 OK.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'successfully deleted'}, status=status.HTTP_200_OK)




class HistoryListView(ListAPIView):
    """
    Представление для отображения списка записей истории, связанных с определенным экземпляром Data_Table.

    Этот класс наследует от ListAPIView и используется для обработки GET-запросов,
    возвращающих список записей истории, связанных с экземпляром Data_Table по его идентификатору.

    Attributes:
        serializer_class (HistorySerializer): Класс сериализатора, используемый для преобразования данных модели History в JSON.

    Methods:
        get_queryset(): Возвращает queryset записей истории, связанных с экземпляром Data_Table по его идентификатору.
        list(request, *args, **kwargs): Обрабатывает GET-запрос и возвращает список записей истории вместе с количеством связанных экземпляров.

    Returns:
        Response: HTTP-ответ, содержащий сериализованные данные записей истории и количество связанных экземпляров.
    """

    serializer_class = HistorySerializer

    def get_queryset(self):
        """
        Возвращает queryset записей истории, связанных с экземпляром Data_Table по его идентификатору.

        Returns:
            QuerySet: Queryset записей истории, отфильтрованных по идентификатору Data_Table.
        """
        data_table_id = self.kwargs['id']
        return History.objects.filter(data_table_id=data_table_id)

    def list(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запрос и возвращает список записей истории вместе с количеством связанных экземпляров.
        related_count нужен для отображения количесва изменений позиции.

        Args:
            request (HttpRequest): HTTP-запрос.

        Returns:
            Response: HTTP-ответ, содержащий сериализованные данные записей истории и количество связанных экземпляров.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        # Получаем количество связанных экземпляров
        related_count = queryset.count()

        # Возвращаем ответ с данными и количеством связанных экземпляров
        return Response({
            'data': serializer.data,
            'related_count': related_count
        })

    

class CheckArticleAPIView(APIView):
    """"
    API-представление для проверки наличия артикула в базе данных.

    Этот класс предоставляет GET-метод для поиска артикула в базе данных и возврата информации о товаре,
    если он найден. Если товар не найден, возвращается ошибка 404.
    """
    def get(self, request, art):
        """ 
        
        Обрабатывает GET-запрос для поиска артикула в базе данных.

        """
        result = check_article(art)
        if result:
            return Response(result)
        return Response({"error": "Товара нет в базе"}, status=status.HTTP_404_NOT_FOUND)   
    