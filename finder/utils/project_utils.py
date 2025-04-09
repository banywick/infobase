from finder.models import Remains, ProjectStatus
from django.db.models import Case, When, Value, CharField

class ProjectUtils:
    # @staticmethod
    # def get_projects_dict(projects_ids):
    #     """
    #     Получает проекты из базы данных по их идентификаторам и преобразует их в словарь.

    #     Аргументы:
    #     projects_ids -- список идентификаторов проектов.

    #     Возвращает:
    #     Словарь, где ключи -- идентификаторы проектов, а значения -- названия проектов.
    #     """
    #     projects = Remains.objects.filter(id__in=projects_ids).values_list('id', 'project')
    #     projects_dict = {project_id: project_name for project_id, project_name in projects}
    #     return projects_dict
    
    @staticmethod
    def get_annotated_remains():

        """
        Возвращает аннотированный QuerySet объектов Remains с добавленным полем 'status_color'.

        Этот метод выполняет следующие шаги:
        1. Получает все статусы из модели ProjectStatus.
        2. Создает условия для аннотации с использованием Case/When, основываясь на проектах и их цветах.
        3. Аннотирует QuerySet объектов Remains, добавляя поле 'status_color', которое определяет цвет статуса.

        Возвращает:
            QuerySet: Аннотированный QuerySet объектов Remains с добавленным полем 'status_color'.
        """
        # Получаем все статусы из ProjectStatus
        statuses = ProjectStatus.objects.all()

        # Создаём условия для аннотации
        cases = []
        for status in statuses:
            cases.append(When(project=status.project_name, then=Value(status.color)))

        # Аннотируем Remains с использованием Case/When
        annotated_remains = Remains.objects.annotate(
            status_color=Case(
                *cases,
                default=Value('gray'),  # Значение по умолчанию, если статус не найден
                output_field=CharField()
            )
        )

        return annotated_remains
    

    @staticmethod
    def get_projects_with_status(projects_ids):
        """
        Получает проекты с их статусами (цветами) из базы данных.
        
        Аргументы:
        projects_ids -- список идентификаторов проектов.
        
        Возвращает:
        Словарь, где ключи - id проектов, значения - словари с названием и цветом статуса.
        Пример: {"64875": {"name": "Проект 1", "status_color": "#FF0000"}}
        """
        # Получаем аннотированные остатки с цветами статусов
        annotated_projects = (
            Remains.objects
            .filter(id__in=projects_ids)
            .annotate(status_color=ProjectUtils.get_status_color_annotation())
            .values('id', 'project', 'status_color')
            .distinct()
        )
        
        # Формируем список с нужной структурой
        return [
            {
                'id': project['id'],
                'name': project['project'],
                'status_color': project['status_color']
            }
                for project in annotated_projects
            ]
        
    
    @staticmethod
    def get_status_color_annotation():
        """
        Создает аннотацию для цвета статуса проекта.
        """
        statuses = ProjectStatus.objects.all()
        cases = [
            When(project=status.project_name, then=Value(status.color))
            for status in statuses
        ]
        return Case(
            *cases,
            default=Value('gray'),
            output_field=CharField()
        )