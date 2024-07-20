from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from custom_auth.forms import CustomUserCreationForm


def landing(request):
    login_form = AuthenticationForm()
    register_form = CustomUserCreationForm()
    return render(request, 'landing_page/landing.html', {'login_form': login_form, 'register_form': register_form})

