from django.urls import path
from .views import AccessDeniedView

urlpatterns = [
    # другие маршруты
    path('', AccessDeniedView.as_view(), name='access_denied'),
]