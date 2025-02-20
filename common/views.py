from django.shortcuts import render
from django.views.generic import TemplateView

class AccessDeniedView(TemplateView):
    """Запрет доступа"""

    template_name = 'common/access-denied.html'
