from django.core.paginator import Paginator
from django.shortcuts import render
from django.utils import timezone
from datetime import date, datetime
from money_management.models import Transaction
from money_management.forms import AccountForm, CURRENCY_CHOICES
from money_management.utils import convert_currency
from concurrent.futures import ThreadPoolExecutor
from .forms import TransactionFilterForm


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
    transactions = Transaction.objects.filter(date=today).order_by('-created_at')
    paginator = Paginator(transactions, 20)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    account_form = AccountForm()
    target_currency = request.GET.get('currency', 'USD')

    with ThreadPoolExecutor() as executor:
        converted_transactions = list(executor.map(lambda t: convert_transaction(t, target_currency), page_obj))

    return render(request, 'reports/today_reports.html', {
        'transactions': converted_transactions,
        'account_form': account_form,
        'target_currency': target_currency,
        'currency_choices': CURRENCY_CHOICES,
        'page_obj': page_obj,
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



def search_transactions(request):
    form = TransactionFilterForm(request.GET or None)
    transactions = Transaction.objects.all()

    if form.is_valid():
        if form.cleaned_data['account']:
            transactions = transactions.filter(account=form.cleaned_data['account'])
        if form.cleaned_data['type']:
            transactions = transactions.filter(type=form.cleaned_data['type'])
        if form.cleaned_data['min_amount']:
            transactions = transactions.filter(amount__gte=form.cleaned_data['min_amount'])
        if form.cleaned_data['max_amount']:
            transactions = transactions.filter(amount__lte=form.cleaned_data['max_amount'])
        if form.cleaned_data['start_date']:
            transactions = transactions.filter(date__gte=form.cleaned_data['start_date'])
        if form.cleaned_data['end_date']:
            transactions = transactions.filter(date__lte=form.cleaned_data['end_date'])
        if form.cleaned_data['category']:
            transactions = transactions.filter(category__icontains=form.cleaned_data['category'])

    transactions = transactions.order_by('-created_at')[:50]

    return render(request, 'reports/search_transactions.html', {
        'form': form,
        'transactions': transactions,
    })

