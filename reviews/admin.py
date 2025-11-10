from django.contrib import admin
from .models import Review

# admin.site.register(Review)
@admin.register(Review)
class ReviewAdminModel(admin.ModelAdmin):
    list_display = ('user','text','created_at')
