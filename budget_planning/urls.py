from django.urls import path
from . import views

app_name = 'budget_planning'

urlpatterns = [
    path('add_budget/', views.add_budget, name='add_budget'),
    path('budgets/', views.budget_list, name='budget_list'),
    path('add_plan/', views.add_plan, name='add_plan'),
    path('plans/', views.plan_list, name='plan_list'),
    path('notifications/', views.notifications, name='notifications'),
]
