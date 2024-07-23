from django import forms
from money_management.models import Account, Transaction

class TransactionFilterForm(forms.Form):
    account = forms.ModelChoiceField(queryset=Account.objects.all(), required=False, label='Аккаунт')
    type = forms.ChoiceField(choices=[('', 'Все'), ('income', 'Доходы'), ('expense', 'Расходы')], required=False, label='Тип')
    min_amount = forms.DecimalField(required=False, label='Минимальная сумма')
    max_amount = forms.DecimalField(required=False, label='Максимальная сумма')
    start_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), required=False, label='Начальная дата')
    end_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), required=False, label='Конечная дата')
    category = forms.CharField(required=False, label='Категория')
