from django.urls import path
from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name='home'),#Главная страница
    path('products/', ProductSearchView.as_view(), name='product_filter'),#Поисковой движок
    path('details/<str:article>/', RemainsDetailView.as_view(), name='position-detail'),#Детализация
    path('projects/', ProjectListView.as_view(), name='project-list'),#Все проекты
    path('get_session_filter_projects/', GetSessionDataView.as_view(), name='get-session-data'),# Все проекты
    path('add_projects_to_session/', AddProjectsToSessionView.as_view(), name='add-projects-to-session'), #Добавление в сессию
    path('clear_selected_projects/', ClearSelectedProjectsView.as_view(), name='clear_selected_projects'),#удалить выбранные проекты
    path('remove_project_from_session/', RemoveProjectFromSessionView.as_view(), name='remove-project-from-session'),#Частично удалить проекты с сессии
]

