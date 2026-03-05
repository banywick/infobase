from django.contrib import admin
from .models import Review, NewsItem

# admin.site.register(Review)
@admin.register(Review)
class ReviewAdminModel(admin.ModelAdmin):
    list_display = ('user','text','created_at')



@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at")
    search_fields = ("title", "description")
    ordering = ("-created_at",)

