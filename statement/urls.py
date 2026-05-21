from django.urls import path
from . import views

from statement.views import *

# Апи для заполнения ведомостей
urlpatterns = [
    path('', StatementHome.as_view(), name='statement_home'),
    path('draw_statement/<path:search_string>/', Statement.as_view(), name='draw_statement'),
    path('job_vk_statement/', views.job_vk, name='job_vk_auto'),
    path('job_vk_async/', views.job_vk_async, name='job_vk_async'),
    path('get-smb-configs/', views.get_smb_config, name='get_smb_configs'),
    
    # Статусы задач
    path('api/task/status/<str:task_id>/', views.get_task_status, name='task_status'),  # ЭТОТ УРЛ НУЖЕН
    path('api/task/cancel/<str:task_id>/', views.cancel_task, name='cancel_task'),
    
    # Индексация
    path('api/smb/index/status/', views.get_index_status, name='get_index_status'),
    path('api/smb/index/stats/', views.get_index_stats, name='get_index_stats'),
    path('api/smb/index/start/', views.start_indexing, name='start_indexing'),
    path('api/smb/index/task/<str:task_id>/', views.get_indexing_task_status, name='get_indexing_task_status'),
    
    # Файлы
    path('api/smb/files/', views.get_indexed_files, name='get_indexed_files'),
    path('api/smb/file-info/', views.get_file_info, name='get_file_info'),
    
    # Обработка
    path('api/smb/process/start/', views.start_processing, name='start_processing'),
    path('api/smb/process/stats/', views.get_processing_stats, name='get_processing_stats'),
]