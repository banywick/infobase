from django.db import models
from finder.models import Remains, ProjectStatus
from django.db.models import Case, When, Value, CharField

class ProjectUtils:
    @staticmethod
    def get_projects_dict(projects_ids):
        """
        Получает проекты из базы данных по их идентификаторам и преобразует их в словарь.

        Аргументы:
        projects_ids -- список идентификаторов проектов.

        Возвращает:
        Словарь, где ключи -- идентификаторы проектов, а значения -- названия проектов.
        """
        projects = Remains.objects.filter(id__in=projects_ids).values_list('id', 'project')
        projects_dict = {project_id: project_name for project_id, project_name in projects}
        return projects_dict
    
    @staticmethod
    def get_annotated_remains():
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