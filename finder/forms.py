from django import forms
from finder.models import Review


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