import json
import logging
from django.db.models import Sum
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from .forms import TransactionForm, AccountForm
from .models import Transaction, Account
from budget_planning.models import  Notification, Plan
from .utils import convert_currency
from .forms import CURRENCY_CHOICES
from concurrent.futures import ThreadPoolExecutor
from django.core.paginator import Paginator
from django.http import JsonResponse


logger = logging.getLogger(__name__)
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
        'date': transaction.date,
        'note': transaction.note,
        'created_at': formatted_created_at,
        'currency': target_currency
    }


def add_transaction(request):
    date_str = request.GET.get('date', '')
    next_url = request.GET.get('next', 'money_management:index')
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            amount = form.cleaned_data['amount']
            currency = form.cleaned_data['currency']
            if currency != 'USD':
                transaction.amount = convert_currency(amount, currency, 'USD')
            transaction.save()
            check_budget(transaction)
            return redirect(next_url)
    else:
        form = TransactionForm(initial={'date': date_str})
    return render(request, 'money_management/add_transaction.html', {'form': form, 'next': next_url})

def add_account(request):
    next_url = request.GET.get('next', 'money_management:index')
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.user = request.user
            account.save()
            return redirect(next_url)
    else:
        form = AccountForm()
    return render(request, 'money_management/add_account.html', {'form': form, 'next': next_url})


def update_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            return redirect('money_management:index')
    else:
        form = TransactionForm(instance=transaction)
    return render(request, 'money_management/update_transaction.html', {'form': form})


def delete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        transaction.delete()
        return redirect('money_management:index')
    return render(request, 'money_management/delete_transaction.html', {'transaction': transaction})

logger = logging.getLogger(__name__)

def index(request):
    try:
        transactions = Transaction.objects.all().order_by('-created_at')
        paginator = Paginator(transactions, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        account_form = AccountForm()
        target_currency = request.GET.get('currency', 'USD')
        account_id = request.GET.get('account', None)
        chart_type = request.GET.get('chart_type', 'line')

        if account_id:
            transactions = transactions.filter(account_id=account_id)

        with ThreadPoolExecutor() as executor:
            converted_transactions = list(executor.map(lambda t: convert_transaction(t, target_currency), page_obj))

        date_field = 'date'
        daily_totals = transactions.extra({'date': "DATE(created_at)"}).values(date_field).annotate(total_amount=Sum('amount')).order_by(date_field)
        income_totals = transactions.filter(type='Income').extra({'date': "DATE(created_at)"}).values(date_field).annotate(total_amount=Sum('amount')).order_by(date_field)
        expense_totals = transactions.filter(type='Expense').extra({'date': "DATE(created_at)"}).values(date_field).annotate(total_amount=Sum('amount')).order_by(date_field)

        chart_data = {
            'labels': [str(item[date_field]) for item in daily_totals],
            'total': [float(item['total_amount']) for item in daily_totals],
            'income': [float(item['total_amount']) for item in income_totals],
            'expense': [float(item['total_amount']) for item in expense_totals],
        }

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'transactions': converted_transactions,
                'has_next': page_obj.has_next(),
                'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None
            })

        return render(request, 'money_management/index.html', {
            'transactions': converted_transactions,
            'account_form': account_form,
            'target_currency': target_currency,
            'currency_choices': CURRENCY_CHOICES,
            'page_obj': page_obj,
            'chart_data': json.dumps(chart_data),
            'chart_type': chart_type,
            'account_id': account_id,
            'accounts': Account.objects.all(),
        })

    except Exception as e:
        logger.error(f"Error in index view: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Internal Server Error', 'details': str(e)}, status=500)


def check_budget(transaction):
    account = transaction.account
    user = account.user
    category = transaction.category

    budgets = Plan.objects.filter(user=user, category=category)
    if budgets.exists():
        budget = budgets.first()
        total_expenses = Transaction.objects.filter(
            account__user=user, category=category
        ).aggregate(total=Sum('amount'))['total'] or 0
        if budget.limit is not None and total_expenses + transaction.amount > budget.limit:
            Notification.create_notification(
                user=user,
                message=f'Вы превысили бюджет для {category}.'
            )
            budget.is_completed = True
            budget.save()

    plans = Plan.objects.filter(user=user)
    for plan in plans:
        total_expenses = Transaction.objects.filter(
            account__user=user
        ).aggregate(total=Sum('amount'))['total'] or 0
        if total_expenses >= plan.amount:
            plan.is_completed = True
            plan.save()
        elif plan.due_date < timezone.now().date():
            plan.is_failed = True
            plan.save()
