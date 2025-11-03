# finance/models.py
# (This is the complete, corrected file)

from django.db import models
from django.contrib.auth.models import User
from projects.models import Project
from django.db.models import Sum, Q
from decimal import Decimal # <-- 1. ADD THIS IMPORT

class Account(models.Model):
    """
    Represents a financial account, e.g., "Main", "Admin Petty Cash", "Sound Dept"
    """
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
    
    @property
    def get_balance(self):
        """
        Calculates the balance by summing all transactions related to this account.
        Credits (money in) are positive. Debits (money out) are negative.
        """
        
        # --- 2. THIS IS THE FIX ---
        # We use Decimal('0.00') instead of the float 0.00
        credits = Transaction.objects.filter(to_account=self).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        debits = Transaction.objects.filter(from_account=self).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        return credits - debits

class Transaction(models.Model):
    """
    The master ledger. Represents a single movement of money.
    """
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    from_account = models.ForeignKey(
        Account, 
        related_name='debits', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True
    )
    to_account = models.ForeignKey(
        Account, 
        related_name='credits', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True
    )
    
    project = models.ForeignKey(
        Project, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    expense = models.OneToOneField(
        'Expense', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )

    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.description} - {self.amount}"

class Expense(models.Model):
    """
    Represents a single expense, now linked to an Account.
    """
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expense_date = models.DateField()
    
    account = models.ForeignKey(
        Account, 
        on_delete=models.PROTECT,
        help_text="The account this expense was paid from."
    )
    
    project = models.ForeignKey(
        Project, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='expenses'
    )
    staff_member = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='expenses'
    )
    receipt = models.FileField(
        upload_to='receipts/', 
        null=True, 
        blank=True,
        help_text="Upload receipt (PDF, JPG, PNG)"
    )
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-expense_date']

    def __str__(self):
        return f"{self.description} - {self.amount}"

class Asset(models.Model):
    """
    For company valuation. Links to an EquipmentItem.
    """
    equipment = models.OneToOneField(
        'equipment.EquipmentItem', 
        on_delete=models.CASCADE,
        related_name='asset_value'
    )
    purchase_value = models.DecimalField(max_digits=10, decimal_places=2)
    current_value = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField()

    def __str__(self):
        return f"{self.equipment.name} - Value: {self.current_value}"