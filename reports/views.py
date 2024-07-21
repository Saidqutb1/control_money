# reports/views.py
from django.shortcuts import render
from django.utils import timezone
from datetime import date, datetime
from money_management.models import Transaction
from money_management.forms import AccountForm, CURRENCY_CHOICES
from money_management.utils import convert_currency
from concurrent.futures import ThreadPoolExecutor


def convert_transaction(transaction, target_currency):
    converted_amount = convert_currency(transaction.amount, 'USD', target_currency)
    return {
        'id': transaction.id,
        'account': transaction.account,
        'type': transaction.get_type_display(),
        'previous_balance': convert_currency(transaction.previous_balance, 'USD', target_currency),
        'amount': converted_amount,
        'current_balance': convert_currency(transaction.current_balance, 'USD', target_currency),
        'category': transaction.category,
        'date': transaction.date,
        'note': transaction.note,
        'currency': target_currency
    }


def today_reports(request):
    today = date.today()
    transactions = Transaction.objects.filter(date=today)
    account_form = AccountForm()
    target_currency = request.GET.get('currency', 'USD')

    with ThreadPoolExecutor() as executor:
        converted_transactions = list(executor.map(lambda t: convert_transaction(t, target_currency), transactions))

    return render(request, 'reports/today_reports.html', {
        'transactions': converted_transactions,
        'account_form': account_form,
        'target_currency': target_currency,
        'currency_choices': CURRENCY_CHOICES,
        'today': today
    })


def month_reports(request):
    today = timezone.now()
    transactions = Transaction.objects.filter(date__year=today.year, date__month=today.month)
    account_form = AccountForm()
    target_currency = request.GET.get('currency', 'USD')

    with ThreadPoolExecutor() as executor:
        converted_transactions = list(executor.map(lambda t: convert_transaction(t, target_currency), transactions))

    return render(request, 'reports/month_reports.html', {
        'transactions': converted_transactions,
        'account_form': account_form,
        'target_currency': target_currency,
        'currency_choices': CURRENCY_CHOICES,
        'today': today
    })


def year_reports(request):
    today = timezone.now()
    transactions = Transaction.objects.filter(date__year=today.year)
    account_form = AccountForm()
    target_currency = request.GET.get('currency', 'USD')

    with ThreadPoolExecutor() as executor:
        converted_transactions = list(executor.map(lambda t: convert_transaction(t, target_currency), transactions))

    return render(request, 'reports/year_reports.html', {
        'transactions': converted_transactions,
        'account_form': account_form,
        'target_currency': target_currency,
        'currency_choices': CURRENCY_CHOICES,
        'today': today
    })


def search_by_date(request):
    if request.method == 'POST':
        date_str = request.POST.get('date')
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            transactions = Transaction.objects.filter(date=selected_date)
            account_form = AccountForm()
            target_currency = request.GET.get('currency', 'USD')

            with ThreadPoolExecutor() as executor:
                converted_transactions = list(
                    executor.map(lambda t: convert_transaction(t, target_currency), transactions))

            return render(request, 'reports/search_results.html', {
                'transactions': converted_transactions,
                'selected_date': selected_date,
                'account_form': account_form,
                'target_currency': target_currency,
                'currency_choices': CURRENCY_CHOICES
            })
        except ValueError:
            return render(request, 'reports/search_by_date.html', {'error': 'Invalid date format'})
    return render(request, 'reports/search_by_date.html')
