from django.urls import path
from . import views

urlpatterns = [
    # Главная страница
    path('', views.TableView.as_view(), name='table'),
    path('special_cars/', views.TableView.as_view(), name='special_cars'),
    
    # API endpoints
    path('api/get-locations/', views.get_locations_api, name='get_locations'),
    path('api/save-row/', views.save_row, name='save_row'),
    path('api/update-row/<int:item_id>/', views.update_row, name='update_row'),
    path('api/delete-row/<int:item_id>/', views.delete_row, name='delete_row'),
    path('api/add-child/', views.add_child, name='add_child'),
    
    # Экспорт отчета
    path('export-report/', views.export_report, name='export_report'),
]
