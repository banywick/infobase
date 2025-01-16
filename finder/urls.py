from django.urls import path
from .views import ProductSearchView, HomeView


urlpatterns = [
    path('', HomeView.as_view(), name='home'),#Главная страница
    path('products/', ProductSearchView.as_view(), name='product_filter'),#Поисковой движок
]

