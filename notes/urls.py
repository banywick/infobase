from django.urls import path
from .views import *

urlpatterns = [
    path('', NotesView.as_view(), name='notes'),
    path('add_note/', AddNoteView.as_view(), name='notes' ),
    path('remove_note/<int:id>/', RemoveNote.as_view(), name ='remove_note'),
    path('all_notes/', GetAllNotes.as_view(), name ='all_notes'),
    path('edit_note/<int:id>/', EditNote.as_view(), name ='edit_note'),

]
