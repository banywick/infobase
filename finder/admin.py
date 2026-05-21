# finder/admin.py

from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.urls import path
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.contrib import messages
from django.utils.html import format_html
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
import pandas as pd
from .models import AccountingData, ProjectStatus, LinkAccess, Remains, Standard, StandardValue
from django import forms
from django.core.exceptions import ValidationError
from .forms import ExcelImportFormEquivalent
import datetime
import time
from django.db import transaction


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
            df = pd.read_excel(excel_file, header=0, keep_default_na=False)
            
            required_columns = ['Группа', 'id', 'Стандарт']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValidationError(f'Отсутствуют обязательные колонки: {", ".join(missing_columns)}')
            
            return df
        except Exception as e:
            raise ValidationError(f'Ошибка чтения файла: {str(e)}')


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


class GroupAdmin(BaseGroupAdmin):
    list_display = ('name', 'get_users')
    search_fields = ('name',)

    def get_users(self, obj):
        return ", ".join([user.username for user in obj.user_set.all()])
    get_users.short_description = 'Пользователи'


admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)


class StandardValueInline(admin.TabularInline):
    model = StandardValue
    extra = 1


def import_excel_optimized(df):
    """
    Импорт для нового формата Excel (оптимизированный с bulk_create)
    """
    created_standards = 0
    created_values = 0
    errors = []
    
    # Используем bulk_create для массовой вставки
    standards_to_create = []
    values_to_create = []
    
    # Получаем существующие записи для быстрой проверки
    existing_standards = set(Standard.objects.values_list('name', flat=True))
    existing_values = set(StandardValue.objects.values_list('value', flat=True))
    
    # Сначала собираем все стандарты для создания
    for index, row in df.iterrows():
        try:
            standard_id = str(row['id']).strip()
            if not standard_id or standard_id == 'nan':
                continue
            
            if standard_id not in existing_standards:
                standards_to_create.append(Standard(name=standard_id))
                existing_standards.add(standard_id)
                created_standards += 1
        except Exception as e:
            errors.append(f"Строка {index + 2}: {str(e)}")
    
    # Массовое создание стандартов
    if standards_to_create:
        Standard.objects.bulk_create(standards_to_create, ignore_conflicts=True)
    
    # Теперь обрабатываем значения
    for index, row in df.iterrows():
        try:
            standard_id = str(row['id']).strip()
            main_standard = str(row['Стандарт']).strip()
            
            if not standard_id or standard_id == 'nan' or not main_standard or main_standard == 'nan':
                continue
            
            # Получаем объект стандарта
            try:
                standard_obj = Standard.objects.get(name=standard_id)
            except Standard.DoesNotExist:
                continue
            
            # Собираем все артикулы
            all_articles = [main_standard]
            
            analog_columns = [col for col in df.columns if col.startswith('Аналог')]
            for analog_col in analog_columns:
                analog_value = str(row[analog_col]).strip()
                if analog_value and analog_value != 'nan' and analog_value != '':
                    all_articles.append(analog_value)
            
            all_articles = list(dict.fromkeys(all_articles))
            
            # Собираем значения для создания
            for article in all_articles:
                if article and article != 'nan' and article not in existing_values:
                    values_to_create.append(StandardValue(standard=standard_obj, value=article))
                    existing_values.add(article)
                    created_values += 1
                    
        except Exception as e:
            errors.append(f"Строка {index + 2}: {str(e)}")
    
    # Массовое создание значений
    if values_to_create:
        # Создаем пачками по 1000 для оптимизации памяти
        batch_size = 1000
        for i in range(0, len(values_to_create), batch_size):
            batch = values_to_create[i:i + batch_size]
            StandardValue.objects.bulk_create(batch, ignore_conflicts=True)
    
    return created_standards, created_values, errors


@admin.register(Standard)
class StandardAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_group_info', 'get_main_standard', 'get_values_count', 'get_view_analogs_link')
    search_fields = ('name', 'values__value')
    inlines = [StandardValueInline]
    change_list_template = 'admin/finder/standard/change_list.html'
    
    def get_group_info(self, obj):
        return "Болт" if obj.name in ['1', '2', '3'] else "Гайка" if obj.name in ['4', '5'] else "Шайба"
    get_group_info.short_description = "Группа"
    
    def get_main_standard(self, obj):
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
        if request.method == 'POST':
            form = ExcelImportForm(request.POST, request.FILES)
            if form.is_valid():
                start_time = time.time()
                try:
                    df = form.cleaned_data['excel_file']
                    created_standards, created_values, errors = import_excel_optimized(df)
                    
                    elapsed_time = time.time() - start_time
                    
                    if errors:
                        for error in errors[:10]:
                            messages.warning(request, error)
                    
                    messages.success(
                        request,
                        f'✅ Импорт завершен за {elapsed_time:.2f} сек!\n'
                        f'📊 Создано стандартов: {created_standards}, артикулов: {created_values}'
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
        standards = Standard.objects.all().order_by('name')
        
        parsed_groups = []
        
        for standard in standards:
            values = standard.values.all()
            group_name = self.get_group_info(standard)
            main_standard = self.get_main_standard(standard)
            
            analogs = [value.value for value in values]
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


# finder/admin.py - только измененная часть для AccountingData

@admin.register(AccountingData)
class AccountingDataAdmin(admin.ModelAdmin):
    list_display = ['accounting_code', 'nomenclature_kd', 'accounting_name']
    search_fields = ['accounting_code', 'nomenclature_kd', 'accounting_name']
    list_filter = ['accounting_code']
    actions = ['export_selected']
    list_per_page = 100
    
    change_list_template = "admin/accounting_data_changelist.html"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-excel/', self.import_excel, name='import_excel'),
            path('export-all/', self.export_all, name='export_all'),
            path('export-csv/', self.export_csv_all, name='export_csv_all'),  # Быстрый экспорт в CSV
        ]
        return custom_urls + urls
    
    def export_all(self, request):
        """Экспорт всех данных в Excel (оптимизированный через pandas)"""
        return self._export_to_excel_optimized(request, "accounting_data_all")
    
    def export_csv_all(self, request):
        """Быстрый экспорт всех данных в CSV"""
        return self._export_to_csv(request, "accounting_data_all")
    
    def export_selected(self, request, queryset):
        """Action для экспорта выбранных записей"""
        return self._export_to_excel_optimized(request, "accounting_data_selected", queryset)
    export_selected.short_description = "Экспортировать выбранные в Excel"
    
    def _export_to_excel_optimized(self, request, filename_prefix, queryset=None):
        """
        Оптимизированный экспорт данных в Excel через pandas
        Работает значительно быстрее для больших объемов данных
        """
        if queryset is None:
            queryset = AccountingData.objects.all().order_by('accounting_code')
        
        if not queryset.exists():
            messages.error(request, "Нет данных для экспорта")
            return redirect('..')
        
        total = queryset.count()
        messages.info(request, f"Начинается экспорт {total} записей...")
        
        start_time = time.time()
        
        # Используем values_list для быстрого получения данных
        data = list(queryset.values_list('accounting_code', 'nomenclature_kd', 'accounting_name'))
        
        # Создаем DataFrame
        df = pd.DataFrame(data, columns=['Код бухгалтерский', 'Номенклатура КД', 'Наименование бухгалтерское'])
        
        # Создаем Excel файл через pandas (быстрее, чем openpyxl вручную)
        output = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{filename_prefix}_{total}_{timestamp}.xlsx"
        output['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Используем pandas для записи Excel
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Accounting Data', index=False)
            
            # Настраиваем ширину колонок
            worksheet = writer.sheets['Accounting Data']
            worksheet.column_dimensions['A'].width = 20
            worksheet.column_dimensions['B'].width = 35
            worksheet.column_dimensions['C'].width = 50
        
        elapsed_time = time.time() - start_time
        messages.success(request, f"✅ Экспорт завершен за {elapsed_time:.2f} сек! Выгружено {total} записей.")
        
        return output
    
    def _export_to_csv(self, request, filename_prefix, queryset=None):
        """
        Экспорт в CSV - самый быстрый вариант для больших объемов
        """
        if queryset is None:
            queryset = AccountingData.objects.all().order_by('accounting_code')
        
        if not queryset.exists():
            messages.error(request, "Нет данных для экспорта")
            return redirect('..')
        
        total = queryset.count()
        messages.info(request, f"Начинается экспорт {total} записей в CSV...")
        
        start_time = time.time()
        
        # Используем values_list для быстрого получения данных
        data = list(queryset.values_list('accounting_code', 'nomenclature_kd', 'accounting_name'))
        
        # Создаем DataFrame
        df = pd.DataFrame(data, columns=['Код бухгалтерский', 'Номенклатура КД', 'Наименование бухгалтерское'])
        
        # Создаем CSV ответ
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{filename_prefix}_{total}_{timestamp}.csv"
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Добавляем BOM для поддержки UTF-8 в Excel
        response.write('\ufeff')
        
        # Записываем CSV
        df.to_csv(response, index=False, encoding='utf-8')
        
        elapsed_time = time.time() - start_time
        messages.success(request, f"✅ Экспорт CSV завершен за {elapsed_time:.2f} сек! Выгружено {total} записей.")
        
        return response
    
    def import_excel(self, request):
        """Оптимизированный импорт данных из Excel для больших объемов"""
        if request.method == 'POST':
            form = ExcelImportFormEquivalent(request.POST, request.FILES)
            if form.is_valid():
                excel_file = request.FILES['excel_file']
                
                try:
                    start_time = time.time()
                    
                    # Чтение Excel файла с оптимизациями
                    if excel_file.name.endswith('.xlsx'):
                        df = pd.read_excel(excel_file, engine='openpyxl')
                    else:
                        df = pd.read_excel(excel_file, engine='xlrd')
                    
                    # Очищаем названия столбцов
                    df.columns = df.columns.str.strip()
                    
                    required_columns = ['Код бухгалтерский', 'Номенклатура КД', 'Наименование бухгалтерское']
                    
                    # Проверяем наличие всех нужных столбцов
                    missing_cols = [col for col in required_columns if col not in df.columns]
                    if missing_cols:
                        messages.error(request, f'В файле отсутствуют столбцы: {", ".join(missing_cols)}')
                        return redirect('..')
                    
                    # Берем только нужные колонки
                    df = df[required_columns]
                    
                    # Оставляем только строки, где ВСЕ три столбца заполнены
                    original_len = len(df)
                    df = df.dropna(subset=required_columns, how='any')
                    after_dropna = len(df)
                    
                    # Удаляем дубликаты
                    df = df.drop_duplicates()
                    duplicates_removed = after_dropna - len(df)
                    
                    messages.info(request, f"📊 Обработка {len(df)} уникальных строк (всего в файле: {original_len})...")
                    
                    # Получаем существующие записи для быстрой проверки
                    existing_records = set(
                        AccountingData.objects.values_list(
                            'accounting_code', 'nomenclature_kd', 'accounting_name'
                        )
                    )
                    
                    # Подготавливаем новые записи для массового создания
                    new_records = []
                    created_count = 0
                    skipped_existing = 0
                    
                    # Обрабатываем данные пачками
                    batch_size = 5000
                    for idx, row in df.iterrows():
                        accounting_code = str(row['Код бухгалтерский']).strip()
                        nomenclature_kd = str(row['Номенклатура КД']).strip()
                        accounting_name = str(row['Наименование бухгалтерское']).strip()
                        
                        if not (accounting_code and nomenclature_kd and accounting_name):
                            continue
                        
                        # Проверяем, существует ли уже такая запись
                        if (accounting_code, nomenclature_kd, accounting_name) not in existing_records:
                            new_records.append(AccountingData(
                                accounting_code=accounting_code,
                                nomenclature_kd=nomenclature_kd,
                                accounting_name=accounting_name
                            ))
                            created_count += 1
                            
                            # Добавляем в существующие, чтобы избежать повторной проверки в этой сессии
                            existing_records.add((accounting_code, nomenclature_kd, accounting_name))
                        else:
                            skipped_existing += 1
                        
                        # Создаем записи пачками для оптимизации памяти
                        if len(new_records) >= batch_size:
                            AccountingData.objects.bulk_create(new_records, ignore_conflicts=True)
                            new_records = []
                    
                    # Создаем оставшиеся записи
                    if new_records:
                        AccountingData.objects.bulk_create(new_records, ignore_conflicts=True)
                    
                    elapsed_time = time.time() - start_time
                    
                    # Формируем сообщения
                    messages.success(
                        request,
                        f'✅ Импорт завершен за {elapsed_time:.2f} сек!\n'
                        f'📊 Добавлено новых записей: {created_count}\n'
                        f'⏭️ Пропущено (уже существовали): {skipped_existing}\n'
                        f'🔄 Удалено дубликатов в файле: {duplicates_removed}'
                    )
                    
                    return redirect('..')
                    
                except Exception as e:
                    messages.error(request, f'❌ Ошибка при обработке файла: {str(e)}')
            else:
                messages.error(request, f'Ошибка валидации формы: {form.errors}')
        else:
            form = ExcelImportFormEquivalent()
        
        context = {
            'form': form,
            'title': 'Импорт данных из Excel',
            'opts': self.model._meta,
        }
        return render(request, 'admin/excel_import_equivalents.html', context)