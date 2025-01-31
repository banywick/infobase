from .project_utils import ProjectUtils


class SessionManager:
    @staticmethod
    def add_projects_to_session(request, projects_ids):
        """
        Добавляет проекты в сессию пользователя.

        Аргументы:
        request -- объект запроса Django.
        projects_ids -- список идентификаторов проектов, которые нужно добавить в сессию.
        пример для js {"projects_ids":["64875","4105"]}

        Метод извлекает проекты из базы данных по их идентификаторам, преобразует их в словарь
        и добавляет в сессию пользователя. Если в сессии уже есть проекты, новые проекты
        добавляются к существующим.
        """

        projects_dict = ProjectUtils.get_projects_dict(projects_ids)
        current_projects = request.session.get('selected_projects', {})
        updated_projects = {**current_projects, **projects_dict}
        request.session['selected_projects'] = updated_projects

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
        Удаляет проект из сессии пользователя по его идентификатору.

        Аргументы:
        request -- объект запроса Django.
        project_id -- идентификатор проекта, который нужно удалить из сессии.

        Метод удаляет проект из сессии пользователя по его идентификатору. Если проект
        существует в сессии, он будет удален.
        """
        # Получаем текущие проекты из сессии или создаем пустой словарь, если их нет
        current_projects = request.session.get('selected_projects', {})

        # Преобразуем project_id в строку
        project_id_str = str(project_id)

        # Удаляем проект по его ID, если он существует
        if project_id_str in current_projects:
            del current_projects[project_id_str]

        # Сохраняем обновленный словарь проектов в сессии
        request.session['selected_projects'] = current_projects


        # Удаляем проект по его ID, если он существует
        if project_id_str in current_projects:
            del current_projects[project_id_str]

        # Сохраняем обновленный словарь проектов в сессии
        request.session['selected_projects'] = current_projects



        