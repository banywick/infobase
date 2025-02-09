from django.urls import path
from .views import *

urlpatterns = [
    path('', ComersView.as_view(), name='home_commers'),
    path('get_all_positions/', AllPositionsView.as_view(), name='all_positions'),
]
