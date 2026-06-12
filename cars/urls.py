from django.urls import path
from . import views

urlpatterns = [
    # Главная страница с таблицей
    path('', views.table_view, name='table'),
    
    # API для сохранения строки
    path('api/save-row/', views.save_row, name='save_row'),
    
    # API для обновления строки
    path('api/update-row/<int:item_id>/', views.update_row, name='update_row'),
    
    # API для удаления строки
    path('api/delete-row/<int:item_id>/', views.delete_row, name='delete_row'),
    
    # API для получения всех записей
    path('api/get-rows/', views.get_rows, name='get_rows'),
    
    # API для получения одной записи
    path('api/get-row/<int:item_id>/', views.get_row, name='get_row'),
]