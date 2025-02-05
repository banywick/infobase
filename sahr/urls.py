from django.urls import path
from .views import *

urlpatterns = [
    path("", SahrView.as_view(), name="sahr_home"),
    path("sahr_find/", SahrFindFilter.as_view(), name = 'find_positions'),
    path("get_all_positions/", GetSahrAllPositions.as_view(), name = 'all_positions'),
    path("add_position/", AddPositions.as_view(), name = 'add_position'),
    path("edit_position/<int:id>/", EditPosition.as_view(), name = 'edit_position'),
    path("remove_position/<int:id>/", RemovePosition.as_view(), name = 'remove_position'),
    path("get_archive/", ArchiveRemovePosition.as_view(), name = 'archive_remove_position'),
    path("get_history/", HistiryEditPositions.as_view(), name = 'history_edit_position'),
    
    # path("check_article/<str:art>", check_article, name="check_article"),
    # path("del_row_sahr/<int:id>", del_row_sahr, name='del_row_sahr'),
    # path('download-excel/', download_backup, name='dowload_backup'),
    # path('history/<int:id>', get_history, name='history'),
    ]