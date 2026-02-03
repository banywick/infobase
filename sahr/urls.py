from django.urls import path
from . import views

urlpatterns = [
    path('', views.SahrView.as_view(), name='sahr_main'),
    path('archive/', views.SahrArchiveView.as_view(), name='sahr_archive'),
    
    # API endpoints
    path('all_positions/', views.GetSahrAllPositions.as_view(), name='all_positions'),
    path('add_position/', views.AddPositions.as_view(), name='add_position'),
    path('edit_position/<int:id>/', views.EditPosition.as_view(), name='edit_position'),
    path('remove_position/<int:id>/', views.RemovePosition.as_view(), name='remove_position'),
    path('history/<int:id>/', views.HistoryListView.as_view(), name='history'),
    path('check-article_form/<str:art>/', views.CheckArticleAPIView.as_view(), name='check_article'),
    path('sahr_find/', views.SahrFindFilter.as_view(), name='sahr_find'),
    path('sahr_find_archive/', views.SahrFindFilterArchive.as_view(), name='sahr_find_archive'),
    path('archive_remove_positions/', views.AllArchiveRemovePosition.as_view(), name='archive_remove_positions'),
    path('backup/', views.SahrBackupView.as_view(), name='backup'),
]