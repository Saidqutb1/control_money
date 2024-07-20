from django.urls import path
from .views import add_transaction, index

urlpatterns = [
    path('', index, name='index'),
    path('add/', add_transaction, name='add_transaction'),
]
