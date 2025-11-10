from django import forms
from finder.models import Review
from django import forms
from django.core.exceptions import ValidationError
import pandas as pd
import io


class InputValue(forms.Form):
    input = forms.CharField(
        label="",
        max_length=50,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "search-input", "placeholder": "Искать здесь...."}
        ),
    )

class ReviewForm(forms.ModelForm):
    user = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите Ваше имя',
        }),
        label='Пользователь'  # Здесь устанавливаем текст для label
    )

    class Meta:
        model = Review
        fields = ['user', 'text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Напишите отзыв',
            }),
        }



class ExcelImportForm(forms.Form):
    excel_file = forms.FileField(
        label='Excel файл',
        help_text='Файл должен содержать колонки: Uni66s, Koholo, Brent и другие'
    )
    
    def clean_excel_file(self):
        excel_file = self.cleaned_data['excel_file']
        
        if not excel_file.name.endswith(('.xlsx', '.xls')):
            raise ValidationError('Файл должен быть в формате Excel (.xlsx или .xls)')
        
        try:
            # Читаем файл
            df = pd.read_excel(excel_file)
            
            # Проверяем обязательные колонки
            required_columns = ['Uni66s', 'Koholo', 'Brent']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValidationError(f'Отсутствуют обязательные колонки: {", ".join(missing_columns)}')
            
            return df
        except Exception as e:
            raise ValidationError(f'Ошибка чтения файла: {str(e)}')        
        





class ExcelImportFormEquivalent(forms.Form):
    excel_file = forms.FileField(
        label='Выберите Excel файл',
        help_text='Файл должен содержать столбцы: Код бухгалтерский, Номенклатура КД, Наименование бухгалтерское'
    )
    
    def clean_excel_file(self):
        excel_file = self.cleaned_data['excel_file']
        
        # Проверка расширения файла
        if not excel_file.name.endswith(('.xlsx', '.xls')):
            raise ValidationError('Файл должен быть в формате Excel (.xlsx или .xls)')
        
        try:
            # Чтение файла
            df = pd.read_excel(excel_file)
            
            # Проверка обязательных столбцов
            required_columns = ['Код бухгалтерский', 'Номенклатура КД', 'Наименование бухгалтерское']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValidationError(
                    f'Отсутствуют обязательные колонки: {", ".join(missing_columns)}'
                )
            
            return excel_file
            
        except Exception as e:
            raise ValidationError(f'Ошибка чтения файла: {str(e)}')