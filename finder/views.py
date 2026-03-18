import logging
import time
import json
import os
import re
from urllib.parse import unquote
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from finder.utils.auto_replace import TransformationString
from finder.utils.filters_q import *
from finder.utils.services.details_service import RemainsDetailService
from .utils.add_session_data import SessionManager
from .models import LinkAccess, Remains
from django.views.generic import TemplateView
from django.db.models import Sum
from .serializers import AccountingDataSerializer, ProjectListSerializer, RemainsSerializer
from .utils.project_utils import ProjectUtils
from finder.tasks import data_save_db, ping 
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import FileUploadSerializer
from .utils.connect_redis_bd import connect_redis
from .utils.file_name_document import get_file_name
from celery.result import AsyncResult
from rest_framework.pagination import PageNumberPagination
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

logger = logging.getLogger(__name__)

class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            doc = serializer.validated_data['doc']
            filename = doc.name

            # Добавляем имя документа в redis
            connect_redis().set('file_name', filename)

            # Определяем путь для сохранения файла
            upload_folder = 'finder/document'
            file_path = os.path.join(upload_folder, filename)

            # Проверяем, существует ли директория, и создаем её, если нет
            os.makedirs(upload_folder, exist_ok=True)

            # Сохраняем файл и запускаем задачу
            with open(file_path, 'wb+') as destination:
                for chunk in doc.chunks():
                    destination.write(chunk)

            task = data_save_db.delay(file_path)
            if task.id:
                # Создаем подключение к Redis
                redis_conn = connect_redis()


                # Сохраняем строку в Redis
                redis_conn.set('task_id', task.id)
                return Response({'message': 'task created',
                                'task_id': task.id}, 
                                status=status.HTTP_202_ACCEPTED)
            return Response({'message': 'Error celery'}, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HomeView(TemplateView):
    """Главная страница"""
    template_name = 'finder/index.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_group = None
        allowed_link_names = []

        if user.is_authenticated:
            user_groups = user.groups.all()
            for group in user_groups:
                user_group = group.name
                break  # Прерываем цикл
            user_groups = user.groups.all()
            allowed_links = LinkAccess.objects.filter(group__in=user_groups)
            allowed_link_names = [link.link_name for link in allowed_links]

        # context['allowed_link_names'] = json.dumps(allowed_link_names)  # Преобразуем в JSON
        context['allowed_link_names'] = json.dumps(allowed_link_names)  # Преобразуем в JSON
        context['user_group'] = user_group
        file_name_context = get_file_name(self.request)
        context.update(file_name_context)
        return context


class ProductSearchView(APIView):


    def post(self, request, *args, **kwargs):
        query = request.data.get('query', '').strip()
        if not query:
            return Response({'message': 'empty input'}, status=status.HTTP_200_OK)

        # Получаем проекты и создаем Q-объекты
        current_projects = get_current_projects(request)
        q_projects = create_q_objects(current_projects, 'project')

        # Создаем Q-объекты для поиска
        search_by_code = request.data.get('search_by_code', False)
        search_by_comment = request.data.get('search_by_comment', False)
        search_by_analog = request.data.get('search_by_analog', False)
        search_by_kd = request.data.get('search_by_kd', False)
        search_terms = query.split()
        
        q_search = create_q_objects_for_query(
            search_terms, 
            search_by_code, 
            search_by_comment,
            search_by_analog
        )

        # Получаем список аналогов
        list_analogs = get_analogs_list(search_terms, search_by_analog)


        #Получаем сопоставление КД\ТН
        list_kd = get_tn_kd(query, search_by_kd)

        # ДОБАВЛЯЕМ: Если нашли коды через КД\ТН, добавляем их в поиск
        if list_kd:
            kd_q_objects = Q()
            for code in list_kd:
                kd_q_objects |= Q(code__iexact=code)  # Замените 'code' на поле в вашей основной таблице
            q_search |= kd_q_objects  # Добавляем к основному поиску
        

        

        # Выполняем запрос
        queryset = ProjectUtils.get_annotated_remains()
        queryset = queryset.filter(q_search & q_projects)

        #Сортировка проектов для группировки
        queryset = queryset.order_by('project')[:500]

        if not queryset.exists():
            return Response({"detail": "Ничего не найдено"}, status=status.HTTP_200_OK)

        serializer = RemainsSerializer(queryset, many=True)
        return Response({
        "results": serializer.data,  # основные результаты
        "analogs": list_analogs,
        # "analogs_kd": list_kd
        }, status=status.HTTP_200_OK)


class StrictPagination(PageNumberPagination):
    page_size = 100  # Жёстко фиксируем 10 элементов на страницу
    page_size_query_param = None  # Запрещаем клиенту менять размер страницы
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data
        })


class AllProdSelectedFilter(APIView):
    pagination_class = StrictPagination  # Используем наш строгий пагинатор

    def post(self, request, *args, **kwargs):
        project_name = request.data.get('project_name')
        if not project_name:
            print('не работает пагинация')
            return Response({"detail": "project_name is required"}, status=status.HTTP_400_BAD_REQUEST)

        queryset = ProjectUtils.get_annotated_remains().filter(
            project=project_name
        ).order_by('id')  # Важно: обязательная сортировка
        
        # Принудительная пагинация ВСЕГДА
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        
        serializer = RemainsSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class RemainsDetailView(APIView):
    """
    Представление для детализации информации о позиции товара по артикулу.

    Предоставляет информацию о:
    - Названии товара.
    - Базовой единице измерения.
    - Общем количестве товара по артикулам.
    - Списке проектов, связанных с этим артикулом.
    - Списке партий, связанных с этим атрикулом.
    - Общем количестве товара по артикулу и выбранному проекту.
    """
    def get(self, request, identifier):
        """
        Обрабатывает GET-запрос для получения детальной информации о товаре
        """
        data = RemainsDetailService.get_remains_detail_data(identifier)
        
        if not data:
            return Response(
                {"error": "Позиция не найдена"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(data, status=status.HTTP_200_OK)


class ProjectListView(APIView):
    """
    Представление для получения списка всех уникальных проектов.

    Предоставляет список проектов, которые используются в системе.
    Каждый проект представлен в виде уникальной записи.
    """

    def get(self, request):
        """
        Обрабатывает GET-запрос для получения списка всех уникальных проектов.

        Параметры:
        - request: Запрос от клиента.

        Возвращает:
        - 200 OK с сериализованным списком уникальных проектов.
        """

           # Получаем аннотированные остатки с полем status_color
        queryset = ProjectUtils.get_annotated_remains()
        
        # Применяем distinct к аннотированному QuerySet
        unique_projects = queryset.distinct('project')
        
        # Сериализуем данные
        serializer = ProjectListSerializer(unique_projects, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class AddProjectsToSessionView(APIView):
    """
    Представление для добавления выбранных проектов в сессию пользователя.

    Этот класс обрабатывает POST-запросы, которые содержат список идентификаторов проектов.
    Проекты добавляются в сессию пользователя с помощью методов класса `SessionManager`.

    Основные функции:
    - Принимает список идентификаторов проектов из тела запроса.
    - Добавляет проекты в сессию пользователя, сохраняя их для дальнейшего использования.
    - Если в сессии уже есть проекты, новые проекты добавляются к существующим.

    Пример JSON-запроса:
    ```json
    {
        "projects_ids": ["64875", "4105"]
    }
    ```

    Методы `SessionManager`, используемые в этом классе:
    - `add_projects_to_session`: Добавляет проекты в сессию пользователя.
    - `clear_selected_projects`: Очищает все выбранные проекты из сессии.
    - `remove_project_from_session`: Удаляет конкретный проект из сессии по его идентификатору.
    """
    def post(self, request):
        """
        Обрабатывает POST-запрос для добавления проектов в сессию пользователя.

        Параметры:
        - request: Запрос от клиента, содержащий JSON с ключом `projects_ids` и списком идентификаторов проектов.

        Возвращает:
        - 200 OK с сообщением "Projects added to session", если проекты успешно добавлены.
        - 400 Bad Request, если список `projects_ids` отсутствует или пуст.

        Пример тела запроса:
        ```json
        {
            "projects_ids": ["64875", "4105"]
        }
        ```

        Логика работы:
        1. Извлекает список идентификаторов проектов из тела запроса.
        2. Использует метод `SessionManager.add_projects_to_session` для добавления проектов в сессию.
        3. Возвращает успешный ответ с сообщением.
        """

        projects_ids = request.data.get('projects_ids')# Список выбранных id проектов
        SessionManager.add_projects_to_session(request, projects_ids)
        return Response({'message': 'Projects added to session'}, status=status.HTTP_200_OK)
    

class GetSessionDataView(APIView):
    """
    Представление для получения данных о выбранных проектах из сессии пользователя.

    Этот класс обрабатывает GET-запросы и возвращает список проектов, которые были ранее
    добавлены в сессию пользователя с помощью класса `AddProjectsToSessionView`.

    Основные функции:
    - Извлекает данные о выбранных проектах из сессии пользователя.
    - Возвращает эти данные в формате JSON.

    Пример ответа:
    ```json
    {
        "selected_projects": {
            "64875": "Название проекта 1",
            "4105": "Название проекта 2"
        }
    }
    ```

    Если в сессии нет данных о выбранных проектах, возвращается пустой список.
    """

    def get(self, request):
        """
        Обрабатывает GET-запрос для получения данных о выбранных проектах из сессии.

        Параметры:
        - request: Запрос от клиента.

        Возвращает:
        - 200 OK с данными о выбранных проектах в формате JSON.
        Если в сессии нет данных, возвращается пустой список.

        Пример ответа:
        ```json
        {
            "selected_projects": {
                "64875": "Название проекта 1",
                "4105": "Название проекта 2"
            }
        }
        ```

        Логика работы:
        1. Извлекает данные из сессии по ключу `selected_projects`.
        2. Если данные отсутствуют, возвращает пустой список.
        3. Возвращает данные в формате JSON.
        """
        session_data = request.session.get('selected_projects', [])
        return Response({'selected_projects': session_data}, status=status.HTTP_200_OK)    
    

class RemoveProjectFromSessionView(APIView):
    """
    Представление для удаления проекта из сессии пользователя.
    Теперь работает с новой структурой данных:
    [
        {"id": 64875, "project": "Проект 1", "status_color": "red"},
        {"id": 4105, "project": "Проект 6", "status_color": "green"}
    ]
    Пример запроса:
        {
            "project_id": 64875  # или "64875" (автоматически конвертируется в int)
        }
    """
    def post(self, request, project_id, *args, **kwargs):
        """
        Обрабатывает POST-запрос для удаления проекта из сессии.
        
        Пример запроса:
        {
            "project_id": 64875  # или "64875" (автоматически конвертируется в int)
        }
        
        Возвращает:
        - 200 OK с обновленным списком проектов, если успешно
        - 400 Bad Request с описанием ошибки, если что-то пошло не так
        """
        print("Received project_id from URL:", project_id)
        try:
            # Конвертируем project_id в int (уже должен быть int из URL)
            project_id = int(project_id)
            
            # Получаем обновленный список проектов после удаления
            updated_projects = SessionManager.remove_project_from_session(request, project_id)
            
            return Response({
                'message': 'Project removed from session',
                'projects': updated_projects
            }, status=status.HTTP_200_OK)
            
        except ValueError:
            return Response(
                {'error': 'Project ID must be a number'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ClearSelectedProjectsView(APIView):
    """
    Представление для полного удаления всех выбранных проектов из сессии пользователя.

    Этот класс обрабатывает POST-запросы и очищает все данные о выбранных проектах,
    которые были сохранены в сессии пользователя, с помощью метода
    `SessionManager.clear_selected_projects`.

    Основные функции:
    - Удаляет все проекты из сессии пользователя.
    - Возвращает сообщение об успешной очистке.

    Пример успешного ответа:
    ```json
    {
        "message": "Selected projects cleared successfully."
    }
    ```

    Используется, когда необходимо сбросить все выбранные проекты и начать с чистого листа.
    """
    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запрос для удаления всех выбранных проектов из сессии пользователя.

        Параметры:
        - request: Запрос от клиента.
        - *args, **kwargs: Дополнительные аргументы (не используются в этом методе).

        Возвращает:
        - 200 OK с сообщением "Selected projects cleared successfully.", если очистка прошла успешно.

        Логика работы:
        1. Использует метод `SessionManager.clear_selected_projects` для удаления всех проектов из сессии.
        2. Возвращает успешный ответ с сообщением.
        """    
        # Используем метод из SessionManager для очистки значений
        SessionManager.clear_selected_projects(request)
        return Response({"message": "Selected projects cleared successfully."}, status=status.HTTP_200_OK)    
    

class AddFixPositionToSession(APIView):
    """
    Представление для добавления фиксированной позиции в сессию пользователя.

    Этот класс предоставляет метод POST для добавления фиксированной позиции в сессию пользователя.
    Метод использует SessionManager для выполнения этой операции.

    Методы:
        post(request, fixed_position_id):
            Обрабатывает POST-запрос для добавления фиксированной позиции в сессию пользователя.

    Аргументы:
        request (HttpRequest): Объект запроса Django.
        fixed_position_id (int): Идентификатор фиксированной позиции, которую нужно добавить в сессию.

    Возвращает:
        Response: Объект ответа с сообщением об успешном добавлении фиксированной позиции.
    """
    def post(self, request, fixed_position_id):
        """
        Обрабатывает POST-запрос для добавления фиксированной позиции в сессию пользователя.

        Аргументы:
            request (HttpRequest): Объект запроса Django.
            fixed_position_id (int): Идентификатор фиксированной позиции, которую нужно добавить в сессию.

        Возвращает:
            Response: Объект ответа с сообщением об успешном добавлении фиксированной позиции.
        """    

        # #Получение по id(fixed_positin_id) аннатированного экзепляра remains c статусом
        SessionManager.add_fix_positions_to_session(request, fixed_position_id)
        return Response({"message": "Fix position add successfully."}, status=status.HTTP_200_OK)
        

class RemoveFixPositionToSession(APIView):
    """
    Представление для удаления фиксированной позиции из сессии пользователя по её идентификатору.

    Этот класс предоставляет метод POST для удаления фиксированной позиции из сессии пользователя.
    Метод использует идентификатор фиксированной позиции для выполнения этой операции.

    Методы:
        post(request, fixed_position_id):
            Обрабатывает POST-запрос для удаления фиксированной позиции из сессии пользователя.

    Аргументы:
        request (HttpRequest): Объект запроса Django.
        fixed_position_id (int): Идентификатор фиксированной позиции, которую нужно удалить из сессии.

    Возвращает:
        Response: Объект ответа с сообщением об успешном удалении фиксированной позиции.
    """
    def post(self, request, fixed_position_id):
        """
        Обрабатывает POST-запрос для удаления фиксированной позиции из сессии пользователя.

        Аргументы:
            request (HttpRequest): Объект запроса Django.
            fixed_position_id (int): Идентификатор фиксированной позиции, которую нужно удалить из сессии.

        Возвращает:
            Response: Объект ответа с сообщением об успешном удалении фиксированной позиции.
        """
        # Меняем тип на string
        fixed_position_id_str = str(fixed_position_id)

        # Получаем текущие проекты из сессии или создаем пустой словарь, если их нет
        current_projects = request.session.get('selected_instance', {})
        # Удаляем проект по его ID, если он существует
        if fixed_position_id_str in current_projects:
            del current_projects[fixed_position_id_str]
            request.session['selected_instance'] = current_projects    
            return Response({"message": "Fix position remove successfully."}, status=status.HTTP_200_OK)  
        

    def delete(self, request):
        """
        Обрабатывает DELETE-запрос для удаления всех фиксированных позиций из сессии.
        
        Аргументы:
            request (HttpRequest): Объект запроса Django.
        
        Возвращает:
            Response: Объект ответа с сообщением об успешном удалении всех позиций.
        """
        # Очищаем словарь с фиксированными позициями
        request.session['selected_instance'] = {}
        
        return Response(
            {"message": "All fixed positions removed successfully."}, 
            status=status.HTTP_200_OK
        )  


class GetFixPositionsToSession(APIView):

    """
    Представление для получения фиксированных позиций из сессии пользователя.

    Этот класс предоставляет метод GET для получения всех фиксированных позиций,
    сохраненных в сессии пользователя.

    Методы:
        get(request):
            Обрабатывает GET-запрос для получения всех фиксированных позиций из сессии пользователя.

    Аргументы:
        request (HttpRequest): Объект запроса Django.

    Возвращает:
        Response: Объект ответа с данными фиксированных позиций, сохраненных в сессии пользователя.
    """
    def get(self, request):
        """
        Обрабатывает GET-запрос для получения всех фиксированных позиций из сессии пользователя.

        Аргументы:
            request (HttpRequest): Объект запроса Django.

        Возвращает:
            Response: Объект ответа с данными фиксированных позиций, сохраненных в сессии пользователя.
        """
        current_projects = request.session.get('selected_instance', {})
        return Response(current_projects, status=status.HTTP_200_OK) 


class CheckTaskStatus(APIView):
    """
    Представление API для проверки статуса выполнения задачи Celery.

    Это представление позволяет проверять текущий статус задачи Celery
    по её идентификатору и возвращает информацию о состоянии задачи.

    Методы
    ------
    get(request)
        Обрабатывает GET-запросы для проверки статуса задачи Celery.

    Атрибуты
    --------
    Нет атрибутов
    """

    def get(self, request):
        """
        Обрабатывает GET-запросы для проверки статуса задачи Celery.

        Этот метод извлекает идентификатор задачи из параметров запроса,
        проверяет статус задачи и возвращает информацию о её состоянии.

        Параметры
        ---------
        request : HttpRequest
            Объект HTTP-запроса.

        Возвращает
        ----------
        Response
            JSON-ответ, содержащий:
            - 'id': Идентификатор задачи.
            - 'status': Статус задачи (например, 'SUCCESS', 'FAILURE', 'PENDING').
            - 'result': Результат выполнения задачи или сообщение об ошибке.
        """
        task_id = request.query_params.get('task_id')

        task_result = AsyncResult(task_id)

        # Проверяем, завершена ли задача
        if task_result.ready():
            if task_result.successful():
                # Если задача успешно завершена
                result = task_result.result
            else:
                # Если задача завершена с ошибкой
                result = str(task_result.result)  # Преобразуем исключение в строку
                connect_redis().set('file_name', 'База не обновлена!')
        else:
            # Если задача еще не завершена
            result = 'Выполняется'

        return Response({
            'id': task_id,
            'status': task_result.status,  # Возвращаем статус задачи
            'result': result,  # Возвращаем результат или сообщение об ошибке
        })


class CeleryStatusView(APIView):
    """
    Представление API для проверки статуса работника Celery.

    Это представление отправляет задачу-пинг работнику Celery и ожидает ответа,
    чтобы определить, работает ли Celery и отвечает ли он.

    Методы
    ------
    get(request, *args, **kwargs)
        Обрабатывает GET-запросы для проверки статуса работника Celery.

    """

    def get(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запросы для проверки статуса работника Celery.

        Этот метод отправляет задачу-пинг работнику Celery и ожидает
        небольшой промежуток времени, чтобы проверить, была ли задача успешной.

        Параметры
        ---------
        request : HttpRequest
            Объект HTTP-запроса.
        *args : tuple
            Дополнительные позиционные аргументы.
        **kwargs : dict
            Дополнительные именованные аргументы.

        Возвращает
        ----------
        Response
            - Если Celery работает, возвращает JSON-ответ со статусом и кодом HTTP 200.
            - Если Celery не отвечает, возвращает JSON-ответ со статусом и кодом HTTP 503.
        """
        # Отправляем задачу-пинг
        # проверяем работает ли celery
        task = ping.delay()

        time.sleep(1)

        # Ждем результата
        result = AsyncResult(task.id)

        if result.successful():
            return Response({"status": "Celery работает"}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "Celery не отвечает"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class AutoFind(APIView):
    def post(self, request, *args, **kwargs):
        try:
            input_text = request.data.get('text', '')
            
            # Проверяем, есть ли такая позиция в nomenclature_kd
            existing_entry = AccountingData.objects.filter(
                nomenclature_kd__iexact=input_text  # iexact для регистронезависимого поиска
            ).first()
            
            if existing_entry:
                # Если нашли, возвращаем исходную строку
                return Response({
                    'status': 'success',
                    'processed_text': input_text,
                    'message': 'Позиция найдена в справочнике',
                    'found_in_db': True
                })
            
            # Если не нашли, обрабатываем через TransformationString
            processed_text = TransformationString.screw(input_text)
            
            return Response({
                'status': 'success',
                'processed_text': processed_text,
                'found_in_db': False
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e),
            }, status=500)
        




class Comparison(APIView):
    def post(self, request):
        # Определяем, какой метод вызывать на основе URL или параметров
        if request.path.endswith('auto-collect/') or request.data.get('action') == 'auto_collect':
            return self.post_auto_collect(request)
        else:
            return self.post_regular(request)
    
    def post_regular(self, request):
        """Обычное сохранение"""
        try:
            data = request.data
            print(data, 'ручное')
            
            # Валидация данных
            if not data.get('accounting_code'):
                return Response(
                    {'error': 'Не указан бухгалтерский код'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not data.get('nomenclature_kd'):
                return Response(
                    {'error': 'Не указана номенклатура КД'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not data.get('accounting_name'):
                return Response(
                    {'error': 'Не указано бухгалтерское наименование'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Проверяем, не является ли nomenclature_kd служебной строкой (очищаем от пробелов)
            skip_pattern = 'Что бы получить наименование воспользуйтесь кнопкой <<АВТОПОИСК>>'
            nomenclature_kd = data.get('nomenclature_kd', '').strip()
            
            # Сравниваем очищенное значение
            if nomenclature_kd == skip_pattern:
                logger.info(f"Пропуск сохранения: nomenclature_kd содержит служебную строку")
                return Response(
                    {
                        'message': 'Сохранение пропущено (служебная строка)',
                        'skipped': True
                    }, 
                    status=status.HTTP_200_OK
                )
            
            # Также проверяем, содержит ли строка паттерн (на случай частичного совпадения)
            if skip_pattern in nomenclature_kd:
                logger.info(f"Пропуск сохранения: nomenclature_kd содержит служебную строку (частичное совпадение)")
                return Response(
                    {
                        'message': 'Сохранение пропущено (служебная строка)',
                        'skipped': True
                    }, 
                    status=status.HTTP_200_OK
                )
            
            # ИЗМЕНЕНО: Проверяем существование записи по ВСЕМ ТРЕМ ПОЛЯМ
            existing_record = AccountingData.objects.filter(
                accounting_code=data['accounting_code'],
                nomenclature_kd=data['nomenclature_kd'],
                accounting_name=data['accounting_name']
            ).first()
            
            if existing_record:
                # Если запись существует - возвращаем информацию, но не обновляем
                logger.info(f"Запись уже существует: {data['accounting_code']} - {data['nomenclature_kd']}")
                return Response(
                    {
                        'message': 'Запись уже существует',
                        'data': {
                            'accounting_code': existing_record.accounting_code,
                            'nomenclature_kd': existing_record.nomenclature_kd,
                            'accounting_name': existing_record.accounting_name
                        },
                        'exists': True
                    }, 
                    status=status.HTTP_200_OK
                )
            else:
                # Создаем новую запись
                serializer = AccountingDataSerializer(data=data)
                
                if serializer.is_valid():
                    serializer.save()
                    logger.info(f"Данные успешно сохранены: {data['accounting_code']}")
                    return Response(
                        {
                            'message': 'Данные успешно сохранены',
                            'data': serializer.data
                        }, 
                        status=status.HTTP_201_CREATED
                    )
                else:
                    logger.error(f"Ошибка валидации: {serializer.errors}")
                    return Response(
                        {'error': serializer.errors}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
        except Exception as e:
            logger.error(f"Ошибка при сохранении данных: {str(e)}")
            return Response(
                {'error': f'Внутренняя ошибка сервера: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post_auto_collect(self, request):
        """Метод для автоматического сбора данных"""
        try:
            data = request.data
            print(data, 'Авто')
            logger.info(f"Получены данные для автосбора: {data}")
            
            # Проверяем наличие всех необходимых полей
            if not data.get('clipboard_text'):
                return Response(
                    {'error': 'Не указан текст из буфера обмена'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not data.get('nomenclature_kd'):
                return Response(
                    {'error': 'Не указана номенклатура КД'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not data.get('accounting_name'):
                return Response(
                    {'error': 'Не указано бухгалтерское наименование'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Проверяем, не является ли nomenclature_kd служебной строкой (очищаем от пробелов)
            skip_pattern = 'Что бы получить наименование воспользуйтесь кнопкой <<АВТОПОИСК>>'
            nomenclature_kd = data.get('nomenclature_kd', '').strip()
            
            # Сравниваем очищенное значение
            if nomenclature_kd == skip_pattern:
                logger.info(f"Автосбор: пропуск сохранения - nomenclature_kd содержит служебную строку")
                return Response(
                    {
                        'message': 'Сохранение пропущено (служебная строка)',
                        'skipped': True
                    }, 
                    status=status.HTTP_200_OK
                )
            
            # Также проверяем, содержит ли строка паттерн (на случай частичного совпадения)
            if skip_pattern in nomenclature_kd:
                logger.info(f"Автосбор: пропуск сохранения - nomenclature_kd содержит служебную строку (частичное совпадение)")
                return Response(
                    {
                        'message': 'Сохранение пропущено (служебная строка)',
                        'skipped': True
                    }, 
                    status=status.HTTP_200_OK
                )
            
            # Извлекаем бухгалтерский код из полного текста
            clipboard_text = data['clipboard_text']
            
            # Пытаемся найти бухгалтерский код в тексте
            # Ищем код в начале строки (цифры, буквы, дефисы, точки, слеши)
            code_pattern = r'^([A-Za-z0-9\-_\.\/]+)'
            code_match = re.match(code_pattern, clipboard_text.strip())
            
            if code_match:
                accounting_code = code_match.group(1)
            else:
                # Если не нашли по шаблону, берем первую часть до пробела или табуляции
                parts = clipboard_text.strip().split()
                accounting_code = parts[0] if parts else "UNKNOWN"
            
            logger.info(f"Извлечен бухгалтерский код: {accounting_code}")
            
            # Подготавливаем данные для сохранения
            save_data = {
                'accounting_code': accounting_code,
                'nomenclature_kd': data['nomenclature_kd'],
                'accounting_name': data['accounting_name']
            }
            
            # ИЗМЕНЕНО: Проверяем существование записи по ВСЕМ ТРЕМ ПОЛЯМ
            existing_record = AccountingData.objects.filter(
                accounting_code=accounting_code,
                nomenclature_kd=data['nomenclature_kd'],
                accounting_name=data['accounting_name']
            ).first()
            
            if existing_record:
                # Если запись существует - возвращаем информацию, но не обновляем
                logger.info(f"Автосбор: запись уже существует: {accounting_code} - {data['nomenclature_kd']}")
                return Response(
                    {
                        'message': 'Запись уже существует',
                        'data': {
                            'accounting_code': existing_record.accounting_code,
                            'nomenclature_kd': existing_record.nomenclature_kd,
                            'accounting_name': existing_record.accounting_name
                        },
                        'exists': True
                    }, 
                    status=status.HTTP_200_OK
                )
            else:
                # Создаем новую запись
                serializer = AccountingDataSerializer(data=save_data)
                
                if serializer.is_valid():
                    serializer.save()
                    logger.info(f"Автосбор: данные сохранены для кода {accounting_code}")
                    
                    return Response(
                        {
                            'message': 'Данные успешно сохранены',
                            'data': serializer.data,
                            'accounting_code': accounting_code
                        }, 
                        status=status.HTTP_201_CREATED
                    )
                else:
                    logger.error(f"Ошибка валидации: {serializer.errors}")
                    return Response(
                        {'error': serializer.errors}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
        except Exception as e:
            logger.error(f"Ошибка при автосборе данных: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Внутренняя ошибка сервера: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

