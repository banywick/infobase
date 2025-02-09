from django.contrib import admin
from .models import ProjectStatus

@admin.register(ProjectStatus)
class ProjectStatusAdmin(admin.ModelAdmin):
    # Поля, которые будут отображаться в списке объектов
    list_display = ('project_name', 'color', 'get_color_display')

    # Поля, по которым можно фильтровать
    list_filter = ('color',)

    # Поля, по которым можно искать
    search_fields = ('project_name',)

    # Поля, которые можно редактировать прямо из списка
    list_editable = ('color',)

    # Настройка формы редактирования
    fieldsets = (
        (None, {
            'fields': ('project_name', 'color')
        }),
    )

    # Метод для отображения человекочитаемого значения color
    def get_color_display(self, obj):
        return obj.get_color_display()
    get_color_display.short_description = 'Цвет'  # Заголовок колонки