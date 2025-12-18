from django import forms
from .models import *

class InputDataForm(forms.Form):
    invoice_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
        'class':'input_wrapper',
        'placeholder': 'Введите номер документа'
        }),
        label='Введите номер документа*'
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={
        'type': 'date',
        'class':'input_wrapper'
        }),
        label='Дата*'
    )

    supplier = forms.ModelChoiceField(
        queryset=Supler.objects.all(),
        widget=forms.Select(attrs={
        'class':'input_wrapper',    
        }),
        empty_label="Выберите вариант",
        label='Выбор поставщика*'
    )

    party_mirror = forms.CharField(
        widget=forms.TextInput(attrs={
        'class':'check_party button_mod_width button button--white',
        'placeholder': 'Артикул'
        }),
        label='Партия*'
    )
    name = forms.CharField(
        widget=forms.TextInput(attrs={
        'class':'views_title input_wrapper',
        'placeholder': 'Автоматическая подстановка наименования'
        }),
        label='Наименование*'
    )

    quantity = forms.FloatField(
        widget=forms.TextInput(attrs={
        'class':'button_mod_width button button--white',    
        'placeholder': 'Количество'
        }),
        label='Введите количество* '
    )
    comment = forms.ModelChoiceField(
        queryset=Comment.objects.all(),
        widget=forms.Select(attrs={
        'class':'input_wrapper', 
        }),
        empty_label="Выберите вариант",
        label='Установите комментарий*'
        
    )
    description_problem = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': ' Опишите проблему',
            'class':'text_area_form'
        }),
        label='Описание проблемы (не обязательно)',
        required=False,  # Явно указываем, что поле не обязательное
    )
    specialist = forms.ModelChoiceField(
        queryset=Specialist.objects.all(),
        widget=forms.Select(attrs={
        'class':'input_wrapper', 
        }),
        empty_label="Выберите вариант",
        label='Принял товар*'
    )
    leading = forms.ModelChoiceField(
        queryset=Leading.objects.all(),
        widget=forms.Select(attrs={
        'class':'input_wrapper',     
        }),
        empty_label="Выберите вариант",
        label='Ведущий накладную*'
    )
    unit = forms.CharField(
        widget=forms.HiddenInput(attrs={'id': 'hidden_unit'})  # Скрытое поле с id
    )
    article = forms.CharField(
        widget=forms.HiddenInput(attrs={'id': 'hidden_article'})  # Скрытое поле с id
    )
    project = forms.CharField(
        widget=forms.HiddenInput(attrs={'id': 'hidden_project'})  # Скрытое поле с id
    )
    party = forms.CharField(
        widget=forms.HiddenInput(attrs={'id': 'hidden_party'})  # Скрытое поле с id
    )




class InvoiceEditForm(forms.ModelForm):
    # Явно объявляем все поля как в InputDataForm
    invoice_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'input_wrapper',
            'placeholder': 'Введите номер документа'
        }),
        label='Номер накладной*'
    )
    
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'input_wrapper'
        }),
        label='Дата*'
    )
    
    supplier = forms.ModelChoiceField(
        queryset=Supler.objects.all(),
        widget=forms.Select(attrs={
            'class': 'input_wrapper',
        }),
        empty_label="Выберите вариант",
        label='Выбор поставщика*'
    )
    
    
    name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'views_title input_wrapper',
            'placeholder': 'Автоматическая подстановка наименования'
        }),
        label='Наименование*'
    )
    
    quantity = forms.FloatField(
        widget=forms.TextInput(attrs={
            'class': 'button_mod_width button button--white',
            'placeholder': 'Количество*'
        }),
        label='Введите количество*'
    )
    
    comment = forms.ModelChoiceField(
        queryset=Comment.objects.all(),
        widget=forms.Select(attrs={
            'class': 'input_wrapper',
        }),
        empty_label="Выберите вариант",
        label='Установите комментарий*'
    )
    
    description_problem = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': ' Опишите проблему',
            'class': 'text_area_form'
        }),
        label='Описание проблемы (не обязательно)',
        required=False,
    )
    
    specialist = forms.ModelChoiceField(
        queryset=Specialist.objects.all(),
        widget=forms.Select(attrs={
            'class': 'input_wrapper',
        }),
        empty_label="Выберите вариант",
        label='Принял товар*'
    )
    
    leading = forms.ModelChoiceField(
        queryset=Leading.objects.all(),
        widget=forms.Select(attrs={
            'class': 'input_wrapper',
        }),
        empty_label="Выберите вариант",
        label='Ведущий накладную*'
    )
    
    # Скрытые поля
    article = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'check_party button_mod_width button button--white',
            'placeholder': 'Артикул*'
        }),
        label='Артикул'
    )
    
    unit = forms.CharField(
        widget=forms.HiddenInput(attrs={'id': 'hidden_unit'}),
        required=False
    )
    
    project = forms.CharField(
        widget=forms.HiddenInput(attrs={'id': 'hidden_project'}),
        required=False
    )
    
    class Meta:
        model = Invoice
        fields = ['invoice_number', 'date', 'supplier', 'article', 'name', 
                'unit', 'quantity', 'comment', 'description_problem', 
                'specialist', 'leading', 'project']

class InvoiceEditFormStatus(forms.ModelForm):
    status = forms.ModelChoiceField(
        queryset=Status.objects.all(),
        widget=forms.Select(attrs={
            'class': 'input_wrapper',
        }),
        label='Выберите статус',
        empty_label="Выберите статус"
    )
    
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'text_area_form',
            'placeholder': 'Введите описание...'
        }),
        label='Описание',
        required=False
    )
    
    class Meta:
        model = Invoice
        fields = ['status', 'description']
        labels = {
            'status': 'Статус',
        }

class FilterForm(forms.Form):
    supplier = forms.ModelChoiceField(
        queryset=Supler.objects.all(),
        required=False,
        label='Поставщик',
        widget=forms.Select(
            attrs={
                'class':'input_wrapper mod_width_input', 
                'placeholder': 'Выберите вариант',
            }
        ),
            empty_label="Выберите вариант",
    )

    leading = forms.ModelChoiceField(
        queryset=Leading.objects.all(),
        required=False,
        label='Ведущий накладную',
        widget=forms.Select(
            attrs={
                'class':'input_wrapper mod_width_input',
                'placeholder': 'Выберите вариант',
            }
        ),
            empty_label="Выберите вариант",
    )

    status = forms.ModelChoiceField(
        queryset=Status.objects.all(),
        required=False,
        label='Статус',
        widget=forms.Select(
            attrs={
                'class':'input_wrapper mod_width_input', 
                'placeholder': 'Выберите вариант',
            }
        ),
            empty_label="Выберите вариант",
    )
    

class AddSupplerForm(forms.ModelForm):
    class Meta:
        model = Supler
        fields = '__all__'  # или перечисли нужные поля, например: fields = ['name', 'other_field']
        labels = {
            'name': 'Название поставщика',
            # Добавь другие лейблы, если нужно
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input_wrapper',
                'placeholder': 'Введите название поставщика'
            }),
            # Добавь другие виджеты, если нужно
        }