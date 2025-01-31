from finder.models import Remains

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