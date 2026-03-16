from django.urls import path

from statement.views import *

# Апи для заполнения ведомостей
urlpatterns = [
    path('', StatementHome.as_view(), name='statement_home'),

    path('draw_statement/<path:search_string>/', Statement.as_view(), name='draw_statement'),

]