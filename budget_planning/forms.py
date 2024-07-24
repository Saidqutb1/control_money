from django import forms
from .models import Plan


class PlanForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ['account', 'type', 'amount', 'category', 'note', 'due_date']
        widgets = {
            'account': forms.Select(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }