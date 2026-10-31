from django import forms

from .models import Review, OrderRequest


class ContactForm(forms.Form):
    name = forms.CharField(label='Имя', max_length=64, widget=forms.TextInput(attrs={'placeholder': 'Ваше имя'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'placeholder': 'Ваш email'}))
    subject = forms.CharField(label='Тема', max_length=128,
                              widget=forms.TextInput(attrs={'placeholder': 'Тема сообщения'}))
    message = forms.CharField(max_length=5000, label='Сообщение', widget=forms.Textarea(attrs={'placeholder': 'Сообщение', 'rows': 5}))


class OrderForm(forms.ModelForm):
    quantity = forms.IntegerField(min_value=1, max_value=10000)
    comment = forms.CharField(required=False, max_length=5000)
    class Meta:
        model = OrderRequest
        fields = ['product', 'customer_name', 'phone', 'quantity', 'comment']
        widgets = {
            'customer_name': forms.TextInput(attrs={'placeholder': 'Ваше имя', 'class': 'form-input', 'autocomplete': 'name', 'required': True}),
            'phone': forms.TextInput(attrs={'type': 'tel', 'inputmode': 'tel', 'placeholder': '+7 (___) ___-__-__', 'class': 'form-input', 'autocomplete': 'tel', 'required': True}),
            'quantity': forms.NumberInput(attrs={'min': 1, 'value': 1, 'inputmode': 'numeric', 'class': 'form-input'}),
            'comment': forms.Textarea(attrs={'placeholder': 'Адрес доставки или комментарий к заказу...', 'rows': 3, 'class': 'form-textarea'}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'text']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Ваше имя',
                'class': 'form-input'
            }),
            'text': forms.Textarea(attrs={
                'placeholder': 'Напишите ваш отзыв...',
                'rows': 4,
                'class': 'form-textarea'
            })
        }
        labels = {
            'name': '',
            'text': ''
        }
