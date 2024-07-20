from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from custom_auth.forms import CustomUserCreationForm
from .forms import TransactionForm, AccountForm
from .models import Transaction

def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = TransactionForm()
    return render(request, 'money_management/add_transaction.html', {'form': form})

def add_account(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.user = request.user
            account.save()
            return redirect('index')
    else:
        form = AccountForm()
    return render(request, 'money_management/add_account.html', {'form': form})

def index(request):
    transactions = Transaction.objects.all()
    account_form = AccountForm()
    login_form = AuthenticationForm()
    register_form = CustomUserCreationForm()
    return render(request, 'money_management/index.html', {'transactions': transactions, 'account_form': account_form, 'login_form': login_form, 'register_form': register_form})
