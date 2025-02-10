from django.urls import path
from .views import *

urlpatterns = [
    # Главная страница
    path('', HomeView.as_view(), name='home'),

    #Загрузка файла xlsx
    path('upload/', FileUploadView.as_view(), name='file-upload'),

    # Поисковой движок
    path('products/', ProductSearchView.as_view(), name='product_filter'),

    # Закрепление позиции
    path('add_positions_to_session/<int:fixed_position_id>/',
        AddFixPositionToSession.as_view(), name='add_fixed_positions'),

    # Удаление позиции
    path('remove_positions_to_session/<int:fixed_position_id>/',
        RemoveFixPositionToSession.as_view(), name='remove_fixed_positions'),

    #Получение закрепленных позиции    
    path('fixed_positions/',
        GetFixPositionsToSession.as_view(), name='get_fixed_positions'),

    #Поисковой движок    
    path('all_products_filter_project/', AllProdSelectedFilter.as_view(), name='product_filter_project'),

    #Детализация позиции по id
    path('details/id/<int:identifier>/', RemainsDetailView.as_view(), name='position-detail_id'),

    #Детализация позиции по артикулу
    path('details/article/<str:identifier>/', RemainsDetailView.as_view(), name='position-detail_article'),

    # Все проекты
    path('projects/', ProjectListView.as_view(), name='project-list'),

    # Все проекты добавленные в сессию
    path('get_session_filter_projects/', GetSessionDataView.as_view(), name='get-session-data'),

    #Добавление в сессию проекта для фильтра
    path('add_projects_to_session/', AddProjectsToSessionView.as_view(), name='add-projects-to-session'), 

    # Удалить все выбранные проекты
    path('clear_selected_projects/', ClearSelectedProjectsView.as_view(), name='clear_selected_projects'),

    #Частично удалить проекты с сессии
    path('remove_project_from_session/', RemoveProjectFromSessionView.as_view(), name='remove-project-from-session'),
]

