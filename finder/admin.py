from django.contrib import admin
from .models import Review, CategoryProduct, Product, Analog

# admin.site.register(Review)
@admin.register(Review)
class ReviewAdminModel(admin.ModelAdmin):
    list_display = ('user','text','created_at')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Поля, которые будут отображаться в списке
    search_fields = ('name',)  # Поля, по которым можно искать
    list_filter = ('name',)  # Поля, по которым можно фильтровать

class AnalogAdmin(admin.ModelAdmin):
    list_display = ('product', 'analog_name', 'category')  # Поля, которые будут отображаться в списке
    search_fields = ('product__name', 'analog_name', 'category__category_product')  # Поля, по которым можно искать
    list_filter = ('product', 'category')  # Поля, по которым можно фильтровать

class CategoryProductAdmin(admin.ModelAdmin):
    list_display = ('category_product',)  # Поля, которые будут отображаться в списке
    search_fields = ('category_product',)  # Поля, по которым можно искать
    list_filter = ('category_product',)  # Поля, по которым можно фильтровать

admin.site.register(Product, ProductAdmin)
admin.site.register(Analog, AnalogAdmin)
admin.site.register(CategoryProduct, CategoryProductAdmin)   