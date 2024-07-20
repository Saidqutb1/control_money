from django.urls import path
from .views import add_transaction, index, add_account, update_transaction, delete_transaction

app_name = 'money_management'

urlpatterns = [
    path('', index, name='index'),
    path('add/', add_transaction, name='add_transaction'),
    path('add_account/', add_account, name='add_account'),
    path('update/<int:pk>/', update_transaction, name='update_transaction'),
    path('delete/<int:pk>/', delete_transaction, name='delete_transaction'),
]
