from django.contrib import admin
from .models import Note

# admin.site.register(Review)
@admin.register(Note)
class ReviewAdminModel(admin.ModelAdmin):
    list_display = ('text',)