from django.urls import path
from . import views

from statement.views import *

# Апи для заполнения ведомостей
urlpatterns = [
    path('', views.StatementHome.as_view(), name='statement_home'),
    path('draw_statement/<path:search_string>/', views.Statement.as_view(), name='draw_statement'),
    path('job_vk_statement/', views.job_vk, name='job_vk_auto'),
    path('get-smb-configs/', views.get_smb_config, name='get_smb_configs'),
    
    # Новые эндпоинты для работы с индексом
    path('api/smb/index/status/', views.get_index_status, name='get_index_status'),
    path('api/smb/index/stats/', views.get_index_stats, name='get_index_stats'),
    path('api/smb/index/start/', views.start_indexing, name='start_indexing'),
    path('api/smb/files/', views.get_indexed_files, name='get_indexed_files'),
    path('api/smb/file-info/', views.get_file_info, name='get_file_info'),
]
