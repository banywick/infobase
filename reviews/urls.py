from django.urls import path
from .views import *


urlpatterns = [
    path('', ReviewsView.as_view(), name='home_review'),
    path('add_review/', AddReview.as_view(), name='add_review'),
]
