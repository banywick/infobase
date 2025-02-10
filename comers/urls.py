from django.urls import path
from .views import *

urlpatterns = [
    path('', ComersView.as_view(), name='home_commers'),
    path('get_all_positions/', GetAllPositions.as_view(), name='all_positions'),
    path('remove_position/<int:id>/', RemovePosition.as_view(), name ='remove_position'),
]   

