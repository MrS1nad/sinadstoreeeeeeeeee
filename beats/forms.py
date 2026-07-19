from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Beat, DownloadRequest


class SignUpForm(UserCreationForm):
    """Форма регистрации — email не обязателен, но полезен для связи с автором."""
    email = forms.EmailField(required=False, label='Email (необязательно)')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class BeatForm(forms.ModelForm):
    class Meta:
        model = Beat
        fields = [
            'title', 'description', 'genre', 'bpm',
            'cover', 'preview_audio', 'full_audio',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class DownloadRequestForm(forms.ModelForm):
    """Форма, которую человек заполняет перед скачиванием полного трека."""

    class Meta:
        model = DownloadRequest
        fields = ['name', 'telegram', 'phone', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Как к тебе обращаться'}),
            'telegram': forms.TextInput(attrs={'placeholder': '@username'}),
            'phone': forms.TextInput(attrs={'placeholder': '+7 900 000-00-00'}),
            'email': forms.EmailInput(attrs={'placeholder': 'you@example.com'}),
        }
