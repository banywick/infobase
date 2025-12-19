from django.contrib import admin
from .models import Comment, Leading, Supler, Status, Specialist, Invoice

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('text',)
    search_fields = ('text',)

@admin.register(Leading)
class LeadingAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Supler)
class SuplerAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Specialist)
class SpecialistAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'date', 'supplier', 'article', 'name', 'unit', 'quantity', 'comment', 'specialist', 'leading', 'status', 'description')
    search_fields = ('invoice_number', 'name', 'article')
    list_filter = ('status', 'date')