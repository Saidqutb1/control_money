from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'id': 'register_username'}),
            'password1': forms.PasswordInput(attrs={'id': 'register_password1'}),
            'password2': forms.PasswordInput(attrs={'id': 'register_password2'}),
        }


class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'id': 'login_username'}),
            'password': forms.PasswordInput(attrs={'id': 'login_password'}),
        }

