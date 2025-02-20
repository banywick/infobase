from django.contrib import admin
from .models import *
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User

@admin.register(ProjectStatus)
class ProjectStatusAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'color')
    search_fields = ('project_name',)
    list_filter = ('color',)
    list_per_page = 20  # Установите количество строк на странице

    # Добавляем возможность редактирования поля color на странице списка
    list_editable = ('color',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Обновляем choices для project_name при каждом запросе формы
        form.base_fields['project_name'].choices = ProjectStatus.get_project_choices()
        return form

@admin.register(LinkAccess)
class LinkAccessAdmin(admin.ModelAdmin):
    list_display = ('group', 'link_name')
    search_fields = ('group__name', 'link_name')
    list_filter = ('group',)
    list_per_page = 50

    # Добавляем возможность редактирования поля link_name на странице списка
    list_editable = ('link_name',)

    def group(self, obj):
        return obj.group.name
    group.short_description = 'Группа'
    group.admin_order_field = 'group__name'

@admin.register(Remains)
class RemainsAdmin(admin.ModelAdmin):
    list_display = ('article', 'title', 'quantity', 'project',)
    search_fields = ('article', 'title',)
    list_filter = ('project',)
    list_per_page = 100  # Установите количество строк на странице



class GroupAdmin(BaseGroupAdmin):
    list_display = ('name', 'get_users')
    search_fields = ('name',)

    def get_users(self, obj):
        # Получаем всех пользователей, связанных с группой
        return ", ".join([user.username for user in obj.user_set.all()])
    get_users.short_description = 'Пользователи'

# Разрегистрируем стандартную админку Group и регистрируем свою
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)