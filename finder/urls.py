from django.urls import path
from .views import *

urlpatterns = [
    # Главная страница
    path('', HomeView.as_view(), name='home_finder'),
    
    #Проверска статуса выполняемой задачи
    path('get_task_upload_status/', CheckTaskStatus.as_view(), name='status_task'),
    
    #Проверка запущен ли celery
    path('celery_status/', CeleryStatusView.as_view(), name='celery_status_check'),

    # Загрузка файла xlsx
    path('upload/', FileUploadView.as_view(), name='file-upload'),

    # Поисковой движок
    path('products/', ProductSearchView.as_view(), name='product_filter'),

    # Закрепление позиции
    path('add_fix_positions_to_session/<int:fixed_position_id>/',
        AddFixPositionToSession.as_view(), name='add_fixed_positions'),

    # Удаление позиции
    path('remove_fix_positions_to_session/<int:fixed_position_id>/',
        RemoveFixPositionToSession.as_view(), name='remove_fixed_positions'),

    # Получение всех закрепленных позиции    
    path('get_fixed_positions/',
        GetFixPositionsToSession.as_view(), name='get_fixed_positions'),

    # Отобразить все позиции выбранного проекта  
    path('all_products_filter_project/', AllProdSelectedFilter.as_view(), name='product_filter_project'),

    # Детализация позиции по артикулу и id
    path('get_details/article_id/<str:identifier>/', RemainsDetailView.as_view(), name='position-detail_article_id'),

    # Получить  все проекты
    path('get_all_projects/', ProjectListView.as_view(), name='project-list'),

    # Все проекты добавленные в сессию
    path('get_session_filter_projects/', GetSessionDataView.as_view(), name='get-session-data'),

    # Добавление в сессию проекта для фильтра
    path('add_projects_to_session/', AddProjectsToSessionView.as_view(), name='add-projects-to-session'), 

    # Отчистить все выбранные проекты
    path('clear_all_selected_projects/', ClearSelectedProjectsView.as_view(), name='clear_selected_projects'),

    #Частично удалить проекты с сессии
    path('remove_project_from_session/<int:project_id>/', RemoveProjectFromSessionView.as_view(), name='remove_project_from_session'),
]

