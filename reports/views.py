from django.core.paginator import Paginator
from django.http import JsonResponse
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
    formatted_date = transaction.date.strftime('%B %d, %Y, %I:%M %p')
    formatted_created_at = transaction.created_at.strftime('%B %d, %Y, %I:%M %p')
    return {
        'id': transaction.id,
        'account': transaction.account.name,
        'type': transaction.get_type_display(),
        'previous_balance': convert_currency(transaction.previous_balance, 'USD', target_currency),
        'amount': converted_amount,
        'current_balance': convert_currency(transaction.current_balance, 'USD', target_currency),
        'category': transaction.category,
        'date': formatted_date,
        'note': transaction.note,
        'created_at': formatted_created_at,
        'currency': target_currency
    }


def get_paginated_transactions(transactions, request, target_currency):
    paginator = Paginator(transactions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    with ThreadPoolExecutor() as executor:
        converted_transactions = list(executor.map(lambda t: convert_transaction(t, target_currency), page_obj))

    return page_obj, converted_transactions


def today_reports(request):
    today = date.today()
    transactions = Transaction.objects.filter(date=today).order_by('-created_at')
    account_form = AccountForm()
    target_currency = request.GET.get('currency', 'USD')

    page_obj, converted_transactions = get_paginated_transactions(transactions, request, target_currency)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'transactions': converted_transactions,
            'has_next': page_obj.has_next()
        })

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
    transactions = Transaction.objects.filter(date__year=today.year, date__month=today.month).order_by('-created_at')
    account_form = AccountForm()
    target_currency = request.GET.get('currency', 'USD')

    page_obj, converted_transactions = get_paginated_transactions(transactions, request, target_currency)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'transactions': converted_transactions,
            'has_next': page_obj.has_next()
        })

    return render(request, 'reports/month_reports.html', {
        'transactions': converted_transactions,
        'account_form': account_form,
        'target_currency': target_currency,
        'currency_choices': CURRENCY_CHOICES,
        'page_obj': page_obj,
        'today': today
    })


def year_reports(request):
    today = timezone.now()
    transactions = Transaction.objects.filter(date__year=today.year).order_by('-created_at')
    account_form = AccountForm()
    target_currency = request.GET.get('currency', 'USD')

    page_obj, converted_transactions = get_paginated_transactions(transactions, request, target_currency)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'transactions': converted_transactions,
            'has_next': page_obj.has_next()
        })

    return render(request, 'reports/year_reports.html', {
        'transactions': converted_transactions,
        'account_form': account_form,
        'target_currency': target_currency,
        'currency_choices': CURRENCY_CHOICES,
        'page_obj': page_obj,
        'today': today
    })


def search_by_date(request):
    selected_date = request.GET.get('date', None)
    target_currency = request.GET.get('currency', 'USD')
    transactions = Transaction.objects.filter(date=selected_date) if selected_date else Transaction.objects.all()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        paginator = Paginator(transactions, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        with ThreadPoolExecutor() as executor:
            transactions_data = list(executor.map(lambda t: convert_transaction(t, target_currency), page_obj.object_list))
        return JsonResponse({
            'transactions': transactions_data,
            'has_next': page_obj.has_next()
        })

    page_obj, converted_transactions = get_paginated_transactions(transactions, request, target_currency)

    return render(request, 'reports/search_by_date.html', {
        'transactions': converted_transactions,
        'currency_choices': CURRENCY_CHOICES,
        'target_currency': target_currency,
        'selected_date': selected_date,
        'page_obj': page_obj,
    })


def search_transactions(request):
    form = TransactionFilterForm(request.GET or None)
    transactions = Transaction.objects.all()
    target_currency = request.GET.get('currency', 'USD')

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

    page_obj, converted_transactions = get_paginated_transactions(transactions, request, target_currency)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'transactions': converted_transactions,
            'has_next': page_obj.has_next()
        })

    return render(request, 'reports/search_transactions.html', {
        'form': form,
        'transactions': page_obj,
        'page_obj': page_obj,
        'currency_choices': CURRENCY_CHOICES,
        'target_currency': target_currency,
    })