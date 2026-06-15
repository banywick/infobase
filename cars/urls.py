from django.urls import path
from . import views

urlpatterns = [
    path('', views.table_view, name='table'),
    path('special_cars/', views.table_view, name='special_cars'),
    
    path('api/save-row/', views.save_row, name='save_row'),
    path('api/update-row/<int:item_id>/', views.update_row, name='update_row'),
    path('api/delete-row/<int:item_id>/', views.delete_row, name='delete_row'),
    path('api/get-locations/', views.get_locations, name='get_locations'),
    path('api/add-child/', views.add_child, name='add_child'),
]