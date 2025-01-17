from django.urls import path
from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name='home'),#Главная страница
    path('products/', ProductSearchView.as_view(), name='product_filter'),#Поисковой движок
    path('positions/<str:article>/', RemainsDetailView.as_view(), name='position-detail'),#Детализация
    path('projects/', ProjectListView.as_view(), name='project-list'),#Все проекты
    path('add-projects-to-session/', AddProjectsToSessionView.as_view(), name='add-projects-to-session'),
    path('get-session-data/', GetSessionDataView.as_view(), name='get-session-data'),
]

