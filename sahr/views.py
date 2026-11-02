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
from .utils.backup_utils import *
from common.utils.access_mixin import UserGroupRequiredMixin
from django.db import transaction
from django.utils import timezone
import itertools
import re



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

class SahrView(UserGroupRequiredMixin, TemplateView):
    """Главная страница САХР"""

    template_name = 'sahr/index.html'
    group_required = ['update_base','sklad']

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
        print(art)
        if result:
            print(result)
            return Response(result)
        return Response({"error": "Товара нет в базе"}, status=status.HTTP_404_NOT_FOUND)   
    

class SahrBackupView(APIView):
    """
    Представление для обработки запросов на скачивание резервной копии
    данных из С.А.ХР

    Этот класс обрабатывает GET-запросы и предоставляет функциональность для создания
    резервной копии данных из базы данных и отправки её пользователю в виде Excel-файла.

    Methods:
        get(request, *args, **kwargs):
            Обрабатывает GET-запрос для скачивания резервной копии данных.

            Args:
                request (HttpRequest): Объект HTTP-запроса.

            Returns:
                HttpResponse: HTTP-ответ с прикрепленным Excel-файлом резервной копии.

            Процесс:
                1. Вызывает функцию `backup_sahr_table()` для создания резервной копии данных.
                2. Использует функцию `handle_backup_download()` для отправки файла пользователю.

    """
    def get(self, request, *args, **kwargs):

        # Вызов функции для создания резервной копии
        file_path, filename = backup_sahr_table()

        # Использование функции из другого модуля для обработки скачивания
        return handle_backup_download(file_path, filename)





# Словарь похожих символов (латиница <-> кириллица)
LAYOUT_MAP = {
    'A': ['A', 'А'], 'B': ['B', 'В'], 'C': ['C', 'С'], 'E': ['E', 'Е'],
    'H': ['H', 'Н'], 'K': ['K', 'К'], 'M': ['M', 'М'], 'O': ['O', 'О'],
    'P': ['P', 'Р'], 'T': ['T', 'Т'], 'X': ['X', 'Х'], 'Y': ['Y', 'У'],
    'a': ['a', 'а'], 'b': ['b', 'в'], 'c': ['c', 'с'], 'e': ['e', 'е'],
    'h': ['h', 'н'], 'k': ['k', 'к'], 'm': ['m', 'м'], 'o': ['o', 'о'],
    'p': ['p', 'р'], 't': ['t', 'т'], 'x': ['x', 'х'], 'y': ['y', 'у']
}

def get_address_variants(address_str):
    """Генерирует все возможные варианты написания адреса (латиница/кириллица)"""
    if not address_str:
        return []
    
    # Разбиваем строку на символы
    chars = list(address_str.upper())
    options = []
    
    for c in chars:
        if c in LAYOUT_MAP:
            options.append(LAYOUT_MAP[c])
        else:
            options.append([c])
            
    # Генерируем все комбинации (декартово произведение)
    variants = [''.join(p) for p in itertools.product(*options)]
    return variants


class BulkReplaceAddressView(APIView):
    def post(self, request, *args, **kwargs):
        old_address = (request.data.get('old_address') or '').strip()
        new_address = (request.data.get('new_address') or '').strip()

        if not old_address or not new_address:
            return Response({"error": "Укажите оба адреса"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Валидация нового адреса (только латиница и цифры)
        if re.search(r'[А-Яа-яЁё]', new_address):
            return Response(
                {"error": "Новый адрес должен содержать только латинские буквы и цифры. Пожалуйста, переключите раскладку."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Генерируем все варианты старого адреса (вдруг там кириллица)
        old_variants = get_address_variants(old_address)
        
        # Ищем позиции по всем возможным вариантам написания
        positions = Data_Table.objects.filter(address__in=old_variants)
        count = positions.count()
        
        if count == 0:
            return Response({"error": f"Позиции с адресом '{old_address}' (включая кириллицу) не найдены"}, status=status.HTTP_404_NOT_FOUND)

        # Проверка конфликтов на новом адресе
        # (Создаем варианты и для нового адреса, чтобы проверить, нет ли там кириллицы)
        new_variants = get_address_variants(new_address)
        existing_parties_on_new = set(Data_Table.objects.filter(address__in=new_variants).values_list('party', flat=True))
        
        conflicts = [{"id": p.id, "article": p.article, "party": p.party} for p in positions if p.party in existing_parties_on_new]

        if conflicts:
            return Response({
                "error": "На новом адресе уже есть позиции с такими же партиями",
                "conflicts": conflicts
            }, status=status.HTTP_409_CONFLICT)

        now = timezone.now()
        with transaction.atomic():
            history_entries = []
            for pos in positions:
                old_comment = pos.comment or ''
                # В историю пишем реальный старый адрес этой позиции
                history_comment = f"[Массовая замена] {pos.address} → {new_address}. " + old_comment
                
                history_entries.append(
                    History(
                        data_table=pos,
                        article=pos.article,
                        party=pos.party,
                        title=pos.title,
                        comment=history_comment,
                        address=pos.address,
                        date=now,
                    )
                )
            
            History.objects.bulk_create(history_entries)
            
            # Обновляем адреса на новый (латинский)
            updated = positions.update(address=new_address)

        return Response({
            "message": f"Адрес заменён у {updated} позиций",
            "updated_count": updated
        }, status=status.HTTP_200_OK)