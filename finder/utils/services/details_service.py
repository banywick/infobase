# services/remains_service.py
from django.db.models import Sum
from finder.models import Remains
from finder.utils.project_utils import ProjectUtils

class RemainsDetailService:
    """Сервис для работы с деталями остатков"""
    
    @staticmethod
    def get_position_by_identifier(identifier):
        """Получение позиции по ID или артикулу"""
        try:
            id = int(identifier)
            return Remains.objects.filter(id=id).first()
        except ValueError:
            return Remains.objects.filter(article=identifier).first()
        
    @classmethod
    def get_total_quantity_by_article_and_project(cls, article, project_name):
        """
        Получение общего количества по артикулу для конкретного проекта
        (для ведомостей)
        
        Args:
            article: артикул товара
            project_name: название проекта
            
        Returns:
            dict: информация о количестве или None если позиции не найдены
        """
        # Получаем все позиции с указанным артикулом
        all_positions = cls.get_all_positions_by_article(article)
        
        if not all_positions.exists():
            return {
                'article': article,
                'project': project_name,
                'total_quantity': 0,
                'message': 'Позиции с указанным артикулом не найдены'
            }
        
        # Получаем title из первой позиции (он одинаков для всех позиций с одним артикулом)
        title = all_positions.first().title
        
        # Фильтруем позиции по проекту и суммируем количество
        project_positions = all_positions.filter(project=project_name)
        total_quantity = project_positions.aggregate(
            total=Sum('quantity')
        )['total'] or 0
        
        # Получаем дополнительную информацию (опционально)
        positions_details = []
        for position in project_positions:
            positions_details.append({
                'id': position.id,
                'party': position.party,
                'quantity': position.quantity,
                'base_unit': position.base_unit
            })
        
        # Получаем цвет статуса для проекта (если нужно)
        queryset = ProjectUtils.get_annotated_remains()
        status_color_obj = queryset.filter(
            project=project_name
        ).first()
        status_color = status_color_obj.status_color if status_color_obj else 'gray'
        
        return {
            'article': article,
            'title': title,  # Добавлено поле title
            'project': project_name,
            'status_color': status_color,
            'total_quantity': total_quantity,
            'positions_count': project_positions.count(),
            'positions_details': positions_details,
            'base_unit': project_positions.first().base_unit if project_positions.exists() else None
    }    
    
    @staticmethod
    def get_all_positions_by_article(article):
        """Получение всех позиций с указанным артикулом"""
        return Remains.objects.filter(article=article)
    
    @staticmethod
    def get_project_colors(positions_queryset):
        """Получение цветов статусов для проектов"""
        queryset = ProjectUtils.get_annotated_remains()
        project_ids = positions_queryset.values_list('project', flat=True).distinct()
        return {
            proj.project: proj.status_color 
            for proj in queryset.filter(project__in=project_ids)
        }
    
    @staticmethod
    def get_project_details(positions_queryset, project_colors):
        """Получение детальной информации по проектам"""
        details = []
        for position in positions_queryset:
            details.append({
                'project': position.project,
                'quantity': position.quantity,
                'base_unit': position.base_unit,
                'status_color': project_colors.get(position.project, 'gray')
            })
        return details
    
    @staticmethod
    def calculate_totals(positions_queryset, project=None):
        """Расчет суммарных количеств"""
        total_quantity = positions_queryset.aggregate(
            total_quantity=Sum('quantity')
        )['total_quantity']
        
        total_by_project = None
        if project:
            print(project, '******')
            total_by_project = positions_queryset.filter(
                project=project
            ).aggregate(total_quantity=Sum('quantity'))['total_quantity']
        
        return {
            'total_quantity': total_quantity,
            'total_by_project': total_by_project
        }
    
    @staticmethod
    def get_related_data(positions_queryset):
        """Получение связанных проектов и партий"""
        return {
            'projects': list(positions_queryset.values_list('project', flat=True).distinct()),
            'parties': list(positions_queryset.values_list('party', flat=True).distinct())
        }
    
    @classmethod
    def get_remains_detail_data(cls, identifier):
        """Основной метод для получения всех данных"""
        position = cls.get_position_by_identifier(identifier)
        if not position:
            return None
        
        all_positions = cls.get_all_positions_by_article(position.article)
        project_colors = cls.get_project_colors(all_positions)
        project_details = cls.get_project_details(all_positions, project_colors)
        totals = cls.calculate_totals(all_positions, position.project)
        related_data = cls.get_related_data(all_positions)
        
        # Получаем цвет статуса для конкретного проекта
        queryset = ProjectUtils.get_annotated_remains()
        status_color_obj = queryset.filter(
            project=position.project
        ).first().status_color if position.project else 'gray'
        
        return {
            'id': position.id,
            'article': position.article,
            'title': position.title,
            'base_unit': position.base_unit,
            'one_project': position.project,
            'status_one_project': status_color_obj,
            'total_quantity': totals['total_quantity'],
            'total_quantity_by_project': totals['total_by_project'],
            'party': related_data['parties'],
            'details_any_projects': project_details,
            'total_sum_any_projects': sum(item['quantity'] for item in project_details)
        }