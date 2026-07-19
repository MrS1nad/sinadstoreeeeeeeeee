from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Beat


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
            'cover', 'preview_audio', 'full_audio', 'price',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_price(self):
        price = self.cleaned_data['price']
        if price <= 0:
            raise forms.ValidationError('Цена должна быть больше нуля.')
        return price
