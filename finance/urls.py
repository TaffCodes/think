# finance/urls.py
# (Create this file)

from django.urls import path
from .views import ExpenseListView, ExpenseCreateView

urlpatterns = [
    path('', ExpenseListView.as_view(), name='expense-list'),
    path('new/', ExpenseCreateView.as_view(), name='expense-create'),
    # We will add URLs for reports, accounts, etc. later
]