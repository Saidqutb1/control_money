from django.shortcuts import render, redirect
from .forms import TransactionForm
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

def index(request):
    transactions = Transaction.objects.all()
    return render(request, 'money_management/index.html', {'transactions': transactions})
