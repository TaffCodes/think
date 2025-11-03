# finance/forms.py
# (Edit this file)

from django import forms
from .models import Expense, Account, Transaction
from projects.models import Project
from django.contrib.auth.models import User

class ExpenseForm(forms.ModelForm):
    # ... (this form is unchanged) ...
    account = forms.ModelChoiceField(
        queryset=Account.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Pay from Account",
        help_text="Select the account this expense was paid from."
    )
    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )
    staff_member = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False,
        label="Staff (for advance/payment)"
    )
    class Meta:
        model = Expense
        fields = [
            'description', 'amount', 'expense_date', 
            'account', 'project', 'staff_member', 'receipt'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'expense_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'receipt': forms.FileInput(attrs={'class': 'form-control'}),
        }


# --- ADD THIS NEW FORM ---
class TransactionForm(forms.ModelForm):
    """
    Form for manually creating a transaction (transfer, deposit, withdrawal).
    """
    # We make these optional to allow for deposits/withdrawals
    from_account = forms.ModelChoiceField(
        queryset=Account.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False,
        label="From Account (Debit)"
    )
    to_account = forms.ModelChoiceField(
        queryset=Account.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False,
        label="To Account (Credit)"
    )
    
    class Meta:
        model = Transaction
        fields = [
            'description', 
            'amount', 
            'from_account', 
            'to_account', 
            'project'
        ]
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'project': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        """
        Validate that either from_account or to_account is filled, but not both empty.
        """
        cleaned_data = super().clean()
        from_account = cleaned_data.get("from_account")
        to_account = cleaned_data.get("to_account")

        if not from_account and not to_account:
            raise forms.ValidationError(
                "A transaction must have at least a 'From' or 'To' account."
            )
        return cleaned_data

# --- ADD THIS NEW FORM ---
class ProjectPaymentForm(forms.Form):
    """
    A simple form to select a project to mark as paid.
    """
    project = forms.ModelChoiceField(
        # We only show projects that are not already paid
        queryset=Project.objects.filter(is_paid=False),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Select Project to Receive Payment For"
    )