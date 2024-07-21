from django.urls import path
from . import views

urlpatterns = [
    path('today/', views.today_reports, name='today_reports'),
    path('month/', views.month_reports, name='month_reports'),
    path('year/', views.year_reports, name='year_reports'),
    path('search/', views.search_by_date, name='search_by_date'),
]
