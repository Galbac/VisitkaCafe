from django import forms

from .models import Review


class ContactForm(forms.Form):
    name = forms.CharField(label='Имя', max_length=64, widget=forms.TextInput(attrs={'placeholder': 'Ваше имя'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'placeholder': 'Ваш email'}))
    subject = forms.CharField(label='Тема', max_length=128, widget=forms.TextInput(attrs={'placeholder': 'Тема сообщения'}))
    message = forms.CharField(label='Сообщение', widget=forms.Textarea(attrs={'placeholder': 'Сообщение', 'rows': 5}))



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