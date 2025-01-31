import logging
from operator import pos
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from finder.utils.filters_q import create_q_objects, create_q_objects_for_query, get_current_projects
from .utils.add_session_data import SessionManager
from .models import Remains
from django.db.models import Q
from django.views.generic import TemplateView
from django.core.cache import cache
from django.db.models import Sum
from .serializers import ProjectListSerializer, RemainsSerializer
from .utils.project_utils import ProjectUtils


logger = logging.getLogger(__name__)

def get_cached_remains_queryset():
    """Создание КЭША из queryset Remains"""
    cache_key = 'remains_all_queryset'
    queryset = cache.get(cache_key)

    if not queryset:
        queryset = Remains.objects.all()
        cache.set(cache_key, queryset, 60 * 60 * 24)
        logger.info("Добавлен в КЭШ!!!!!")
    return queryset


class HomeView(TemplateView):
    """Главня станица"""
    logger.info("HELLLOO")
    template_name = 'index.html'

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
        current_projects = get_current_projects(request)

        # Создаем Q объекты из проектов на основе этих значений
        q_objects_projects = create_q_objects(current_projects, 'project')

        # Попытка получить данные из кэша
        queryset = Remains.objects.all()

        # Разделение ввода на слова
        values = query.split()
        if not values:
            return Response({'message': 'empty input'}, status=status.HTTP_200_OK)

        # Создание Q-объектов для каждого слова
        q_objects = create_q_objects_for_query(values, search_by_code, search_by_comment)

        # Применение фильтров отображаем 200 позиций
        queryset = queryset.filter(q_objects & q_objects_projects)[:200]

        serializer = RemainsSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)  
    
class AllProdSelectedFilter(APIView):
    """
    APIView для фильтрации позиций на основе выбранных проектов.

    Методы:
    post(self, request, *args, **kwargs)
        Обрабатывает POST-запрос для фильтрации позиций на основе выбранных проектов.
    """

    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запрос для фильтрации позиций на основе выбранных проектов.

        Аргументы:
        request -- объект запроса Django.

        Возвращает:
        Response -- объект ответа Django REST Framework с сериализованными данными позиций.

        Пример запроса:
        {
            "projects_ids": ["64875", "4105"]
        }

        Описание:
        1. Получает список выбранных идентификаторов проектов из запроса.
        2. Извлекает из базы данных названия проектов по их идентификаторам и возвращает словарь {id: project_name}.
        3. Преобразует значения словаря в список для функции create_q_objects.
        4. Создает Q-объекты из проектов на основе списка названий проектов.
        5. Выполняет запрос на все позиции и применяет фильтры.
        6. Сериализует данные и возвращает ответ.
        """
        # Список выбранных id проектов получаем с request
        projects_ids = request.data.get('projects_ids')

        # извлекает из базы по id названия и возвращает dict {id:project_name}
        current_projects = ProjectUtils.get_projects_dict(projects_ids)

        # Преобразуем значения словаря в список для функции create_q_objects
        project_names = list(current_projects.values())

        # Создаем Q объекты из проектов на основе current_projects
        q_objects_projects = create_q_objects(project_names, 'project')
        # print(q_objects_projects)

        # Запрос на все позиции
        queryset = Remains.objects.all()

        # Применение фильтров
        queryset = queryset.filter(q_objects_projects)[:200]

        #Серелизуем данные
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
    def get(self, request, id):
        """
        Обрабатывает GET-запрос для получения детальной информации о товаре по артикулу.

        Параметры:
        - request: Запрос от клиента.
        - id: id товара, по которому требуется получить информацию.

        Возвращает:
        - 200 OK с детализированной информацией о товаре, если товар найден.
        - 404 Not Found, если товар с указанным артикулом не найден.
        """

        # Получаем все позиции с указанным артикулом
        positions = Remains.objects.filter(id=id).first()

        #Нужен кверисет что бы сделать агрегацию
        all_positions_by_article = Remains.objects.filter(article=positions.article)

        # Извлекаем значение поля title и base_unit
        # filter используется вместо get на всякий случай
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
        projects = all_positions_by_article.values_list('project', flat=True).distinct()
        partys = all_positions_by_article.values_list('party', flat=True).distinct()

        #Создаем словарь с данными для ответа
        data = {
            'article': article,
            'title': title,
            'base_unit': base_unit,
            'one_project': project,
            'total_quantity': total_quantity,
            'total_quantity_by_project': total_quantity_by_project,
            'projects': list(projects),
            'party': list(partys)
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

        # Получаем все уникальные проекты
        unique_projects = Remains.objects.all().distinct('project')

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
    Представление для частичного удаления проекта из сессии пользователя по его идентификатору.

    Этот класс обрабатывает POST-запросы, которые содержат идентификатор проекта,
    и удаляет соответствующий проект из сессии пользователя с помощью метода
    `SessionManager.remove_project_from_session`.

    Основные функции:
    - Принимает идентификатор проекта из тела запроса.
    - Удаляет проект из сессии пользователя, если он существует.
    - Возвращает сообщение об успешном удалении или ошибку, если идентификатор проекта не передан.

    Пример JSON-запроса:
    ```json
    {
        "project_id": "64875"
    }
    ```

    Пример успешного ответа:
    ```json
    {
        "message": "Project removed from session"
    }
    ```

    Пример ошибки:
    ```json
    {
        "error": "Project ID is required"
    }
    ```
    """
    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запрос для удаления проекта из сессии пользователя.

        Параметры:
        - request: Запрос от клиента, содержащий JSON с ключом `project_id`.
        - *args, **kwargs: Дополнительные аргументы (не используются в этом методе).

        Возвращает:
        - 200 OK с сообщением "Project removed from session", если проект успешно удален.
        - 400 Bad Request с сообщением "Project ID is required", если идентификатор проекта не передан.

        Пример тела запроса:
        ```json
        {
            "project_id": "64875"
        }
        ```

        Логика работы:
        1. Извлекает идентификатор проекта из тела запроса.
        2. Проверяет, передан ли идентификатор проекта. Если нет, возвращает ошибку 400.
        3. Использует метод `SessionManager.remove_project_from_session` для удаления проекта из сессии.
        4. Возвращает успешный ответ с сообщением.
        """
        project_id = request.data.get('project_id')
        if not project_id:
            return Response({'error': 'Project ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        SessionManager.remove_project_from_session(request, project_id)

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
    




