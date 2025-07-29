from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(label='Имя', max_length=64, widget=forms.TextInput(attrs={'placeholder': 'Ваше имя'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'placeholder': 'Ваш email'}))
    subject = forms.CharField(label='Тема', max_length=128, widget=forms.TextInput(attrs={'placeholder': 'Тема сообщения'}))
    message = forms.CharField(label='Сообщение', widget=forms.Textarea(attrs={'placeholder': 'Сообщение', 'rows': 5})) 