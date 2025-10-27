# finance/admin.py
# (Create this file)

from django.contrib import admin
from .models import Account, Expense

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'balance')
    search_fields = ('name',)
    readonly_fields = ('balance',) # Balance should be updated by transactions

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        'description', 
        'amount', 
        'expense_date', 
        'project', 
        'staff_member', 
        'added_by'
    )
    list_filter = ('expense_date', 'project', 'staff_member')
    search_fields = (
        'description', 
        'project__company_name', 
        'staff_member__username'
    )
    autocomplete_fields = ['project', 'staff_member', 'added_by']