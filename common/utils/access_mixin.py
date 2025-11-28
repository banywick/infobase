from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect

class UserGroupRequiredMixin(UserPassesTestMixin):
    """Миксин для проверки принадлежности пользователя к одной из требуемых групп."""

    group_required = ['juls']  # Этот список должен быть переопределен в представлении и содержать имена групп

    def test_func(self):
        """
        Проверяет, принадлежит ли пользователь хотя бы одной из указанных групп.
        Возвращает True, если пользователь принадлежит хотя бы одной группе из списка group_required.
        """
        print(self.request.user.groups)
        return any(self.request.user.groups.filter(name=group).exists() for group in self.group_required)

    def handle_no_permission(self):
        print(self.request.user.groups)
        """
        Обрабатывает ситуацию, когда у пользователя нет доступа.
        Перенаправляет пользователя на страницу 'access_denied', если он не принадлежит ни к одной из требуемых групп.
        """
        return redirect('access_denied')
