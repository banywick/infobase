from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.urls import path
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.contrib import messages
from django.utils.html import format_html
import pandas as pd
from .models import AccountingData, ProjectStatus, LinkAccess, Remains, Standard, StandardValue
from django import forms
from django.core.exceptions import ValidationError
from .forms import ExcelImportFormEquivalent  # Импортируем вашу форму

# Форма для импорта Excel
class ExcelImportForm(forms.Form):
    excel_file = forms.FileField(
        label='Excel файл',
        help_text='Загрузите Excel файл с колонками: Группа, id, Стандарт, Аналог 1...'
    )
    
    def clean_excel_file(self):
        excel_file = self.cleaned_data['excel_file']
        
        if not excel_file.name.endswith(('.xlsx', '.xls')):
            raise ValidationError('Файл должен быть в формате Excel (.xlsx или .xls)')
        
        try:
            # Читаем файл
            df = pd.read_excel(excel_file, header=0, keep_default_na=False)
            
            # Проверяем обязательные колонки
            required_columns = ['Группа', 'id', 'Стандарт']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValidationError(f'Отсутствуют обязательные колонки: {", ".join(missing_columns)}')
            
            return df
        except Exception as e:
            raise ValidationError(f'Ошибка чтения файла: {str(e)}')

# Ваши существующие модели админки
@admin.register(ProjectStatus)
class ProjectStatusAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'color')
    search_fields = ('project_name',)
    list_filter = ('color',)
    list_per_page = 20
    list_editable = ('color',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['project_name'].choices = ProjectStatus.get_project_choices()
        return form

@admin.register(LinkAccess)
class LinkAccessAdmin(admin.ModelAdmin):
    list_display = ('group', 'link_name')
    search_fields = ('group__name', 'link_name')
    list_filter = ('group',)
    list_per_page = 50
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
    list_per_page = 100

# Кастомная админка для Group
class GroupAdmin(BaseGroupAdmin):
    list_display = ('name', 'get_users')
    search_fields = ('name',)

    def get_users(self, obj):
        return ", ".join([user.username for user in obj.user_set.all()])
    get_users.short_description = 'Пользователи'

admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)

# Standard и StandardValue админки
class StandardValueInline(admin.TabularInline):
    model = StandardValue
    extra = 1

def import_excel_optimized(df):
    """
    Импорт для нового формата Excel без GROUP_INFO
    """
    created_standards = 0
    created_values = 0
    errors = []
    
    for index, row in df.iterrows():
        try:
            group_name = str(row['Группа']).strip()
            standard_id = str(row['id']).strip()
            main_standard = str(row['Стандарт']).strip()
            
            if not standard_id or standard_id == 'nan' or not main_standard or main_standard == 'nan':
                continue
            
            # Создаем стандарт с ID из колонки id
            standard, created_std = Standard.objects.get_or_create(name=standard_id)
            if created_std:
                created_standards += 1
            
            # Собираем все артикулы (стандарт + аналоги)
            all_articles = [main_standard]
            
            # Добавляем аналоги из колонок Аналог 1, Аналог 2, etc.
            analog_columns = [col for col in df.columns if col.startswith('Аналог')]
            for analog_col in analog_columns:
                analog_value = str(row[analog_col]).strip()
                if analog_value and analog_value != 'nan' and analog_value != '':
                    all_articles.append(analog_value)
            
            # Удаляем дубликаты
            all_articles = list(dict.fromkeys(all_articles))
            
            # Сохраняем каждый артикул как отдельное значение
            for article in all_articles:
                if article and article != 'nan':
                    article_value, created_art = StandardValue.objects.get_or_create(
                        standard=standard,
                        value=article
                    )
                    if created_art:
                        created_values += 1
                        
        except Exception as e:
            errors.append(f"Строка {index + 2}: {str(e)}")
    
    return created_standards, created_values, errors

@admin.register(Standard)
class StandardAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_group_info', 'get_main_standard', 'get_values_count', 'get_view_analogs_link')
    search_fields = ('name', 'values__value')
    inlines = [StandardValueInline]
    change_list_template = 'admin/finder/standard/change_list.html'
    
    def get_group_info(self, obj):
        """Получаем информацию о группе из первого артикула или по логике"""
        # Если у стандарта есть значения, берем группу из контекста
        # Или можно определить по имени стандарта
        return "Болт" if obj.name in ['1', '2', '3'] else "Гайка" if obj.name in ['4', '5'] else "Шайба"
    get_group_info.short_description = "Группа"
    
    def get_main_standard(self, obj):
        """Получаем основной стандарт - первое значение"""
        first_value = obj.values.first()
        return first_value.value if first_value else "Не указано"
    get_main_standard.short_description = "Основной стандарт"
    
    def get_values_count(self, obj):
        return obj.values.count()
    get_values_count.short_description = "Кол-во артикулов"
    
    def get_view_analogs_link(self, obj):
        return format_html('<a href="view-analogs/" class="button">👁️ Просмотр</a>')
    get_view_analogs_link.short_description = "Детали"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-excel/', self.import_excel, name='import_excel'),
            path('download-template/', self.download_template, name='download_template'),
            path('view-analogs/', self.view_analogs, name='view_analogs'),
        ]
        return custom_urls + urls
    
    def import_excel(self, request):
        """Кастомная view для импорта Excel"""
        if request.method == 'POST':
            form = ExcelImportForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    df = form.cleaned_data['excel_file']
                    created_standards, created_values, errors = import_excel_optimized(df)
                    
                    if errors:
                        for error in errors:
                            messages.warning(request, error)
                    
                    messages.success(
                        request,
                        f'✅ Успешно импортировано! '
                        f'Стандартов: {created_standards}, '
                        f'артикулов: {created_values}'
                    )
                    
                    return HttpResponseRedirect('../')
                
                except Exception as e:
                    messages.error(request, f'❌ Ошибка при импорте: {str(e)}')
        else:
            form = ExcelImportForm()
        
        context = {
            'form': form,
            'title': 'Импорт аналогов из Excel',
            'opts': self.model._meta,
        }
        return render(request, 'admin/excel_import.html', context)
    
    def download_template(self, request):
        """Генерация и скачивание шаблона Excel"""
        import pandas as pd
        from django.http import HttpResponse
        
        template_data = {
            'Группа': ['Болт', 'Болт', 'Болт', 'Гайка', 'Гайка', 'Шайба'],
            'id': [1, 2, 3, 4, 5, 6],
            'Стандарт': ['7808', '37.001.101', '3033', '37.001.124', '5916', '11371'],
            'Аналог 1': ['7796', '7798', '14724', '5915', '439', '125'],
            'Аналог 2': ['', '7805', '14725', '5927', '', '126'],
            'Аналог 3': ['', '931', '444', '934', '', '7089'],
            'Аналог 4': ['', '933', '', '4032', '', '7090'],
            'Аналог 5': ['', '4014', '', '', '', ''],
        }
        
        df = pd.DataFrame(template_data)
        
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="template_analogs.xlsx"'
        
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Аналоги', index=False)
            
            worksheet = writer.sheets['Аналоги']
            worksheet.column_dimensions['A'].width = 10
            worksheet.column_dimensions['B'].width = 8
            worksheet.column_dimensions['C'].width = 20
            for col in ['D', 'E', 'F', 'G', 'H']:
                worksheet.column_dimensions[col].width = 15
        
        return response
    
    def view_analogs(self, request):
        """Просмотр загруженных аналогов в виде таблицы"""
        standards = Standard.objects.all().order_by('name')
        
        parsed_groups = []
        
        for standard in standards:
            values = standard.values.all()
            
            # Определяем группу по логике или контексту
            group_name = self.get_group_info(standard)
            main_standard = self.get_main_standard(standard)
            
            # Собираем все артикулы
            analogs = [value.value for value in values]
            
            # Убираем основной стандарт из списка аналогов для чистоты отображения
            analogs_display = [a for a in analogs if a != main_standard]
            
            parsed_groups.append({
                'id': standard.name,
                'group': group_name,
                'standard': main_standard,
                'analogs': analogs_display,
                'all_values': analogs,
                'values_count': len(analogs)
            })
        
        context = {
            'title': 'Загруженные аналоги',
            'opts': self.model._meta,
            'groups': parsed_groups,
            'groups_count': len(parsed_groups),
        }
        return render(request, 'admin/view_analogs.html', context)
        # """Просмотр загруженных аналогов в виде таблицы"""
        # standards = Standard.objects.all().order_by('name')
        
        # parsed_groups = []
        
        # for standard in standards:
        #     values = standard.values.all()
            
        #     # Определяем группу по логике или контексту
        #     group_name = self.get_group_info(standard)
        #     main_standard = self.get_main_standard(standard)
            
        #     # Собираем все артикулы
        #     analogs = [value.value for value in values]
            
        #     # Убираем основной стандарт из списка аналогов для чистоты отображения
        #     analogs_display = [a for a in analogs if a != main_standard]
            
        #     parsed_groups.append({
        #         'id': standard.name,
        #         'group': group_name,
        #         'standard': main_standard,
        #         'analogs': analogs_display,
        #         'all_values': analogs,
        #         'values_count': len(analogs)
        #     })
        
        # context = {
        #     'title': 'Загруженные аналоги',
        #     'opts': self.model._meta,
        #     'groups': parsed_groups,
        #     'groups_count': len(parsed_groups),
        # }
        # return render(request, 'admin/view_analogs.html', context)

@admin.register(AccountingData)
class AccountingDataAdmin(admin.ModelAdmin):
    list_display = ['accounting_code', 'nomenclature_kd', 'accounting_name']
    search_fields = ['accounting_code', 'nomenclature_kd', 'accounting_name']
    
    change_list_template = "admin/accounting_data_changelist.html"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-excel/', self.import_excel, name='import_excel'),
        ]
        return custom_urls + urls
    
    def import_excel(self, request):
        if request.method == 'POST':
            form = ExcelImportFormEquivalent(request.POST, request.FILES)  # Используем вашу форму
            if form.is_valid():
                excel_file = request.FILES['excel_file']
                
                try:
                    # Чтение Excel файла
                    df = pd.read_excel(excel_file)
                    
                    # Берем только нужные столбцы (игнорируем лишние)
                    required_columns = ['Код бухгалтерский', 'Номенклатура КД', 'Наименование бухгалтерское']
                    df = df[required_columns]
                    
                    # Удаляем пустые строки
                    df = df.dropna()
                    
                    # Создание объектов
                    created_count = 0
                    updated_count = 0
                    errors = []
                    
                    for index, row in df.iterrows():
                        try:
                            accounting_code = str(row['Код бухгалтерский']).strip()
                            nomenclature_kd = str(row['Номенклатура КД']).strip()
                            accounting_name = str(row['Наименование бухгалтерское']).strip()
                            
                            # Пропускаем строки с пустыми значениями
                            if not all([accounting_code, nomenclature_kd, accounting_name]):
                                continue
                            
                            # Создание или обновление записи
                            obj, created = AccountingData.objects.update_or_create(
                                accounting_code=accounting_code,
                                defaults={
                                    'nomenclature_kd': nomenclature_kd,
                                    'accounting_name': accounting_name
                                }
                            )
                            
                            if created:
                                created_count += 1
                            else:
                                updated_count += 1
                                
                        except Exception as e:
                            errors.append(f"Строка {index + 2}: {str(e)}")
                            continue
                    
                    # Сообщения о результате
                    if created_count > 0:
                        messages.success(request, f'Успешно создано записей: {created_count}')
                    if updated_count > 0:
                        messages.info(request, f'Обновлено записей: {updated_count}')
                    if errors:
                        messages.error(request, f'Ошибки при обработке {len(errors)} записей')
                        for error in errors[:10]:
                            messages.warning(request, error)
                    else:
                        messages.success(request, 'Импорт завершен успешно!')
                    
                    return redirect('..')
                    
                except Exception as e:
                    messages.error(request, f'Ошибка при обработке файла: {str(e)}')
        else:
            form = ExcelImportFormEquivalent()  # Используем вашу форму
        
        context = {
            'form': form,
            'title': 'Импорт данных из Excel',
            'opts': self.model._meta,
        }
        return render(request, 'admin/excel_import_equivalents.html', context)
        if request.method == 'POST':
            form = ExcelImportForm(request.POST, request.FILES)
            if form.is_valid():
                excel_file = request.FILES['excel_file']
                
                try:
                    # Чтение Excel файла
                    df = pd.read_excel(excel_file)
                    
                    # Берем только нужные столбцы (игнорируем лишние)
                    required_columns = ['Код бухгалтерский', 'Номенклатура КД', 'Наименование бухгалтерское']
                    df = df[required_columns]
                    
                    # Удаляем пустые строки
                    df = df.dropna()
                    
                    # Создание объектов
                    created_count = 0
                    updated_count = 0
                    errors = []
                    
                    for index, row in df.iterrows():
                        try:
                            accounting_code = str(row['Код бухгалтерский']).strip()
                            nomenclature_kd = str(row['Номенклатура КД']).strip()
                            accounting_name = str(row['Наименование бухгалтерское']).strip()
                            
                            # Пропускаем строки с пустыми значениями
                            if not all([accounting_code, nomenclature_kd, accounting_name]):
                                continue
                            
                            # Создание или обновление записи
                            obj, created = AccountingData.objects.update_or_create(
                                accounting_code=accounting_code,
                                defaults={
                                    'nomenclature_kd': nomenclature_kd,
                                    'accounting_name': accounting_name
                                }
                            )
                            
                            if created:
                                created_count += 1
                            else:
                                updated_count += 1
                                
                        except Exception as e:
                            errors.append(f"Строка {index + 2}: {str(e)}")
                            continue
                    
                    # Сообщения о результате
                    if created_count > 0:
                        messages.success(request, f'Успешно создано записей: {created_count}')
                    if updated_count > 0:
                        messages.info(request, f'Обновлено записей: {updated_count}')
                    if errors:
                        messages.error(request, f'Ошибки при обработке {len(errors)} записей')
                        for error in errors[:10]:
                            messages.warning(request, error)
                    else:
                        messages.success(request, 'Импорт завершен успешно!')
                    
                    return redirect('..')
                    
                except Exception as e:
                    messages.error(request, f'Ошибка при обработке файла: {str(e)}')
        else:
            form = ExcelImportForm()
        
        context = {
            'form': form,
            'title': 'Импорт данных из Excel',
            'opts': self.model._meta,
        }
        return render(request, 'admin/excel_import_equivalents.html', context)