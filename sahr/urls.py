from django.urls import path
from .views import *

urlpatterns = [
    path("", SahrView.as_view(), name="sahr_home"),
    path("archive/", SahrArchiveView.as_view(), name = 'get_archive_page'),
    path("get_archive_all_positions/", AllArchiveRemovePosition.as_view(), name="get_sahr_archive_all"),
    path("find_archive_position/", SahrFindFilterArchive.as_view(), name = 'find_positions_archive'),

    path("sahr_find/", SahrFindFilter.as_view(), name = 'find_positions'),
    path("get_all_positions/", GetSahrAllPositions.as_view(), name = 'all_positions'),
    path("add_position/", AddPositions.as_view(), name = 'add_position'),
    path("edit_position/<int:id>/", EditPosition.as_view(), name = 'edit_position'),
    path("remove_position/<int:id>/", RemovePosition.as_view(), name = 'remove_position'),
    path("get_history_position/<int:id>/", HistoryListView.as_view(), name = 'history_position'),
    path('check-article_form/<str:art>/', CheckArticleAPIView.as_view(), name='check-article'),
    
    # path("check_article/<str:art>", check_article, name="check_article"),
    # path('download-excel/', download_backup, name='dowload_backup'),
    ]