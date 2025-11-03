# finance/urls.py
# (Edit this file)

from django.urls import path
from .views import (
    ExpenseListView, 
    ExpenseCreateView,
    AccountListView,          # <-- ADD
    TransactionCreateView,    # <-- ADD
    ProjectPaymentView,       # <-- ADD
)

urlpatterns = [
    # --- THIS IS THE NEW MAIN PAGE ---
    path('', AccountListView.as_view(), name='account-list'), 
    
    path('expenses/', ExpenseListView.as_view(), name='expense-list'),
    path('expenses/new/', ExpenseCreateView.as_view(), name='expense-create'),
    
    # --- ADD NEW URLS ---
    path('transactions/new/', TransactionCreateView.as_view(), name='transaction-create'),
    path('payment/', ProjectPaymentView.as_view(), name='project-payment'),
]