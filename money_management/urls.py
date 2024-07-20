from django.urls import path
from .views import add_transaction, index, add_account

urlpatterns = [
    path('', index, name='index'),
    path('add/', add_transaction, name='add_transaction'),
    path('add_account/', add_account, name='add_account'),
]
