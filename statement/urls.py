from django.urls import path
from . import views

from statement.views import *

# Апи для заполнения ведомостей
urlpatterns = [
    path('', StatementHome.as_view(), name='statement_home'),

    path('draw_statement/<path:search_string>/', Statement.as_view(), name='draw_statement'),
    path('get-vk-files/', views.get_vk_files, name='get_vk_files'),
    path('job_vk_statement/', views.job_vk, name='job_vk_auto'),
    path('get-smb-configs/', views.get_smb_config, name='get_smb_configs'),

]