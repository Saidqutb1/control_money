# views.py
from django.shortcuts import render, redirect
from .forms import TransactionForm, AccountForm
from .models import Transaction
from .utils import convert_currency

def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            amount = form.cleaned_data['amount']
            currency = form.cleaned_data['currency']
            if currency != 'USD':
                transaction.amount = convert_currency(amount, currency, 'USD')
            transaction.save()
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
    return render(request, 'money_management/index.html', {'transactions': transactions, 'account_form': account_form})

    converted_transactions = []
    for transaction in transactions:
        converted_amount = convert_currency(transaction.amount, 'USD', target_currency)
        converted_transactions.append({
            'account': transaction.account,
            'type': transaction.get_type_display(),
            'previous_balance': convert_currency(transaction.previous_balance, 'USD', target_currency),
            'amount': converted_amount,
            'current_balance': convert_currency(transaction.current_balance, 'USD', target_currency),
            'category': transaction.category,
            'date': transaction.date,
            'note': transaction.note,
            'currency': target_currency
        })

    return render(request, 'money_management/index.html', {
        'transactions': converted_transactions,
        'account_form': account_form,
        'target_currency': target_currency,
        'currency_choices': CURRENCY_CHOICES
    })