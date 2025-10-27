# finance/forms.py
# (Create this file)

from django import forms
from .models import Expense
from projects.models import Project
from django.contrib.auth.models import User

class ExpenseForm(forms.ModelForm):
    """
    Form for creating a new expense.
    """
    
    # We make these fields not required, as they are blank=True
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
            'description', 
            'amount', 
            'expense_date', 
            'project', 
            'staff_member', 
            'receipt'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'expense_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'receipt': forms.FileInput(attrs={'class': 'form-control'}),
        }