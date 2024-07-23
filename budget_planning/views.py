from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Budget, Plan, Notification
from .forms import BudgetForm, PlanForm

@login_required
def add_budget(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            return redirect('budget_planning:budget_list')
    else:
        form = BudgetForm()
    return render(request, 'budget_planning/add_budget.html', {'form': form})

@login_required
def budget_list(request):
    budgets = Budget.objects.filter(user=request.user)
    return render(request, 'budget_planning/budget_list.html', {'budgets': budgets})

@login_required
def add_plan(request):
    if request.method == 'POST':
        form = PlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.user = request.user
            plan.save()
            return redirect('budget_planning:plan_list')
    else:
        form = PlanForm()
    return render(request, 'budget_planning/add_plan.html', {'form': form})

@login_required
def plan_list(request):
    plans = Plan.objects.filter(user=request.user)
    return render(request, 'budget_planning/plan_list.html', {'plans': plans})

@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    return render(request, 'budget_planning/notifications.html', {'notifications': notifications})
