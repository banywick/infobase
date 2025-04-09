from django.http import JsonResponse
from .project_utils import ProjectUtils
from django.forms.models import model_to_dict


class SessionManager:
    @staticmethod
    def add_projects_to_session(request, projects_ids):
        """
        Добавляет проекты с их статусами в сессию пользователя.
        
        Аргументы:
        request -- объект запроса Django.
        projects_ids -- список идентификаторов проектов.
        """
        projects_with_status = ProjectUtils.get_projects_with_status(projects_ids)
        current_projects = request.session.get('selected_projects', [])
        
        # Объединяем текущие проекты с новыми, избегая дубликатов
        existing_ids = {p['id'] for p in current_projects}
        new_projects = [
            p for p in projects_with_status 
            if p['id'] not in existing_ids
        ]
        
        request.session['selected_projects'] = current_projects + new_projects
        return request.session['selected_projects']

    @staticmethod
    def clear_selected_projects(request):
        """
        Очищает все выбранные проекты из сессии пользователя.

        Аргументы:
        request -- объект запроса Django.

        Метод удаляет ключ 'selected_projects' из сессии пользователя, если он существует.
        """
        # Очистка значений по ключу 'selected_projects'
        if 'selected_projects' in request.session:
            del request.session['selected_projects']

    @staticmethod
    def remove_project_from_session(request, project_id):
        """
        Удаляет проект из сессии пользователя.
        
        Аргументы:
        - request: объект запроса Django
        - project_id: ID проекта (int)
        
        Возвращает:
        - Обновленный список проектов в сессии
        """
        current_projects = request.session.get('selected_projects', [])
        
        # Фильтруем проекты, оставляя только те, чей ID не совпадает с удаляемым
        updated_projects = [
            p for p in current_projects 
            if p.get('id') != project_id
        ]
        
        request.session['selected_projects'] = updated_projects
        return updated_projects

    def add_fix_positions_to_session(request, fixed_position_id):
        """
        Добавляет фиксированную позицию в сессию пользователя.

        Этот метод выполняет следующие шаги:
        1. Получает аннотированные данные со статусом из модели Remains.
        2. Ищет экземпляр в базе данных по указанному идентификатору.
        3. Преобразует экземпляр модели в словарь.
        4. Добавляет аннотированные поля в словарь.
        5. Добавляет или обновляет фиксированную позицию в сессии пользователя.

        Аргументы:
            request (HttpRequest): Объект запроса Django.
            fixed_position_id (int): Идентификатор фиксированной позиции, которую нужно добавить в сессию.
        """

        # Получаем аннатированные данные со статусом
        annotated_remains = ProjectUtils.get_annotated_remains()


        # Ищем экземпляр в базе по id(fixed_positin_id)
        try:
            fixed_position = annotated_remains.get(id=fixed_position_id)
        except annotated_remains.model.DoesNotExist:
            return None
        
        # Преобразуем экземпляр модели в словарь
        fixed_position_dict = model_to_dict(fixed_position)

        # Добавляем аннотированные поля в словарь
        fixed_position_dict['status_color'] = fixed_position.status_color

        # Логика добавления в сессию
        current_positions = request.session.get('selected_instance', {})
        current_positions[fixed_position_id] = fixed_position_dict
        request.session['selected_instance'] = current_positions


        