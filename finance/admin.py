# finance/admin.py
# (Edit this file)

from django.contrib import admin
from .models import Account, Expense, Transaction, Asset

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    # --- MODIFIED ---
    list_display = ('name', 'get_balance') # Use the property
    search_fields = ('name',)
    readonly_fields = ('get_balance',) # Make the property readonly

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        'description', 
        'amount', 
        'expense_date', 
        'account', # <-- ADDED
        'project', 
        'staff_member', 
        'added_by'
    )
    list_filter = ('expense_date', 'account', 'project', 'staff_member') # <-- ADDED account
    search_fields = (
        'description', 
        'project__company_name', 
        'staff_member__username',
        'account__name' # <-- ADDED
    )
    autocomplete_fields = ['project', 'staff_member', 'added_by', 'account'] # <-- ADDED account

# --- NEW REGISTRATION ---
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'timestamp', 
        'description', 
        'amount', 
        'from_account', 
        'to_account', 
        'project', 
        'expense'
    )
    list_filter = ('timestamp', 'from_account', 'to_account', 'project')
    search_fields = ('description', 'project__company_name', 'expense__description')
    autocomplete_fields = ['from_account', 'to_account', 'project', 'expense']

# --- NEW REGISTRATION ---
@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = (
        'equipment', 
        'purchase_value', 
        'current_value', 
        'purchase_date'
    )
    search_fields = ('equipment__name',)
    autocomplete_fields = ['equipment']