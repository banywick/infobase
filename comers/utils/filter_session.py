from comers.models import Supler, Leading, Status

class ComersSessionManager:
    @staticmethod
    def get_filter_ids_to_session(request):
        """Получаем id для фильтрации comers из сесии"""
        leading_id = request.session.get('leading_id')
        supplier_id = request.session.get('supplier_id')
        status_id = request.session.get('status_id')
        return [leading_id, supplier_id, status_id]
    @staticmethod
    def get_filter_name_field(request):
        # Получаем значения из сессии
        leading_id = request.session.get('leading_id')
        supplier_id = request.session.get('supplier_id')
        status_id = request.session.get('status_id')

        # Инициализируем переменные для хранения имен
        leading_name = None
        supplier_name = None
        status_name = None

        # Проверяем наличие значений и получаем имена
        if leading_id:
            leading = Leading.objects.filter(id=leading_id).first()
            leading_name = leading.name if leading else None

        if supplier_id:
            supplier = Supler.objects.filter(id=supplier_id).first()
            supplier_name = supplier.name if supplier else None

        if status_id:
            status = Status.objects.filter(id=status_id).first()
            status_name = status.name if status else None

        # Возвращаем имена в виде словаря
        return {
            'leading_name': leading_name,
            'supplier_name': supplier_name,
            'status_name': status_name,
        }
        

