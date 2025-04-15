import logging
import time
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from finder.utils.filters_q import create_q_objects, create_q_objects_for_query, get_current_projects
from .utils.add_session_data import SessionManager
from .models import LinkAccess, Remains
from django.views.generic import TemplateView
from django.db.models import Sum
from .serializers import ProjectListSerializer, RemainsSerializer
from .utils.project_utils import ProjectUtils
from finder.tasks import data_save_db, ping 
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import FileUploadSerializer
import os
from .utils.connect_redis_bd import connect_redis
from .utils.file_name_document import get_file_name
from celery.result import AsyncResult



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

                return Response({'message': 'task created', 'task_id': task.id}, status=status.HTTP_202_ACCEPTED)
            return Response({'message': 'Error celery'}, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HomeView(TemplateView):
    """Главная страница"""
    template_name = 'finder/index2.html'
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
    """
    Представление для поиска товаров с использованием фильтров и условий поиска.
    Поддерживает поиск по коду товара, комментарию и другим параметрам.
    """
    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запрос для поиска товаров.

        Извлекает из request.data параметры поиска:
        - query: строка запроса, которая разделяется на отдельные слова.
        - search_by_code: флаг, указывающий, нужно ли искать по коду товара.
        - search_by_comment: флаг, указывающий, нужно ли искать по комментарию.

        Формирует Q-объекты для фильтрации товаров на основе переданных параметров.
        Применяет фильтры к данным и возвращает результат в виде сериализованного JSON.

        Возвращает:
        - 200 OK с результатами поиска, если запрос успешен.
        - 200 OK с сообщением 'empty input', если запрос пуст.
        """
        query = request.data.get('query', '')
        search_by_code = request.data.get('search_by_code', False)
        search_by_comment = request.data.get('search_by_comment', False)


        # Получаем текущие проекты из сессии
        # По которым будем делать фильтрацию
        current_projects = get_current_projects(request)

        # Создаем Q объекты из проектов на основе этих значений
        q_objects_projects = create_q_objects(current_projects, 'project')

        # Аннатированные данные проект с цветом
        queryset = ProjectUtils.get_annotated_remains()

        # Разделение ввода на слова
        values = query.split()
        if not values:
            return Response({'message': 'empty input'}, status=status.HTTP_200_OK)

        # Создание Q-объектов для каждого слова
        q_objects = create_q_objects_for_query(values, search_by_code, search_by_comment)

        queryset = queryset.filter(q_objects & q_objects_projects)[:200]

        if not queryset.exists():
            return Response({"detail": "Ничего не найдено"}, status=status.HTTP_200_OK)

        serializer = RemainsSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)  

class AllProdSelectedFilter(APIView):
    """
    API endpoint для фильтрации товарных позиций по конкретному проекту.
    
    Позволяет получить аннотированный список остатков товаров с цветовой меткой статуса
    для указанного проекта. Возвращает данные в формате, готовом для отображения в интерфейсе.

    Методы:
    --------
    post(self, request, *args, **kwargs)
        Обрабатывает POST-запрос с названием проекта и возвращает отфильтрованные данные
    """

    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запрос для получения товарных позиций конкретного проекта.

        Параметры запроса:
        ------------------
        request.data : dict
            Должен содержать параметр:
            - project_name: str (название проекта для фильтрации)

        Возвращает:
        -----------
        Response
            - HTTP 200: успешный ответ с данными в формате:
            {
                "id": int,
                "project": str,
                "status_color": str,
                ... другие поля модели Remains
            }[]
            - HTTP 400: если не указан project_name
            - HTTP 404: если проект не найден

        Логика работы:
        --------------
        1. Получает название проекта из request.data
        2. Фильтрует аннотированный queryset (с цветами статусов) по project_name
        3. Сериализует данные с помощью RemainsSerializer
        4. Возвращает отфильтрованные данные

        Пример запроса:
        ---------------
        POST /finder/all_products_filter_project/
        {
            "project_name": "Склад Общий"
        }

        Пример успешного ответа:
        ------------------------
        HTTP 200 OK
        [
            {
                "id": 1,
                "project": "Склад Общий",
                "status_color": "red",
                ...
            },
            ...
        ]
        """
        #получаем название проекта для фильтрации с request
        project_name = request.data.get('project_name')

        queryset = ProjectUtils.get_annotated_remains()
        queryset = queryset.filter(project=project_name)

        serializer = RemainsSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK) 

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
        по артикулу и id

        Параметры:
        - request: Запрос от клиента.
        - id: identifier товара, по которому требуется получить информацию.
        - article: identifier товара, по которому требуется получить информацию.

        Возвращает:
        - 200 OK с детализированной информацией о товаре, если товар найден.
        - 404 Not Found, если товар с указанным артикулом не найден.
        """

        try:
            # Попробуем преобразовать identifier в число
            id = int(identifier)
            positions = Remains.objects.filter(id=id).first()
        except ValueError:
            # Если преобразование не удалось, значит это артикул
            positions = Remains.objects.filter(article=identifier).first()

        if not positions:
            return Response({"error": "Позиция не найдена"}, status=status.HTTP_404_NOT_FOUND)

        #Нужен кверисет что бы сделать агрегацию
        all_positions_by_article = Remains.objects.filter(article=positions.article)
        details_any_projects = []
        for p in all_positions_by_article:
            project_details = {
                'project': p.project,
                'quantity': p.quantity,
                'base_unit': p.base_unit
    }
            # Добавляем словарь в список
            details_any_projects.append(project_details)

        # Вычисление суммы всех проектов
        total_sum_any_projects = sum(item['quantity'] for item in details_any_projects)


            

        # Извлекаем значение поля title и base_unit
        # filter используется вместо get на всякий случай
        id = positions.id if  positions else None
        article = positions.article if  positions else None
        title = positions.title if positions else None
        base_unit = positions.base_unit if positions else None
        project = positions.project if  positions.project else None

        #Суммируем количество по одинаковым артикулам
        total_quantity = all_positions_by_article.aggregate(total_quantity=Sum('quantity'))['total_quantity']
        #Суммируем количество по одинаковым артикулам на конкретном проекте(на который кликнул пользователь)
        total_quantity_by_project = all_positions_by_article.filter(project=project).aggregate(total_quantity=Sum('quantity'))['total_quantity']

        if total_quantity is None:
            return Response({"error": "Position not found"}, status=status.HTTP_404_NOT_FOUND)

        # # Получаем все проекты и партии, связанные с этим артикулом
        project_list = all_positions_by_article.values_list('project', flat=True).distinct()
        partys = all_positions_by_article.values_list('party', flat=True).distinct()

        # Получаем QuerySet с аннотированными остатками (уже содержит status_color)
        queryset = ProjectUtils.get_annotated_remains()

        # Создаем список проектов с их цветами статусов
        projects_with_colors = []
        for project_name in project_list:
            project_data = queryset.filter(project=project_name).first()
            projects_with_colors.append({
                'name': project_name,
                'status_color': project_data.status_color if project_data else 'gray'
            })

        status_color_obj = queryset.filter(project=project).first()

        #Создаем словарь с данными для ответа
        data = {
            'id': id,
            'article': article,
            'title': title,
            'base_unit': base_unit,
            'one_project': project,
            'total_quantity': total_quantity,
            'total_quantity_by_project': total_quantity_by_project,
            'projects': projects_with_colors,  # Теперь это список словарей с цветами
            'party': list(partys),
            'details_any_projects': details_any_projects,
            'total_sum_any_projects': total_sum_any_projects
        }
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
