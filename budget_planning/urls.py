from django.urls import path
from .views import (PlanListView, PlanCreateView, PlanDeleteView, NotificationListView, NotificationDeleteView)

app_name = 'budget_planning'

urlpatterns = [
    path('plans/', PlanListView.as_view(), name='plan_list'),
    path('plans/add/', PlanCreateView.as_view(), name='add_plan'),
    path('plans/delete/<int:pk>/', PlanDeleteView.as_view(), name='delete_plan'),
    path('notifications/', NotificationListView.as_view(), name='notifications'),
    path('notifications/delete/<int:pk>/', NotificationDeleteView.as_view(), name='delete_notification'),
]

