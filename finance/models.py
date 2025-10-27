# finance/models.py
# (Create this file)

from django.db import models
from django.contrib.auth.models import User
from projects.models import Project

class Account(models.Model):
    """
    Represents a financial account, e.g., "Main", "Admin Petty Cash", "Sound Dept"
    """
    name = models.CharField(max_length=100, unique=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Expense(models.Model):
    """
    Represents a single expense, either for the office or a project.
    """
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expense_date = models.DateField()
    
    # Links (can be blank if it's a general office expense)
    project = models.ForeignKey(
        Project, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='expenses'
    )
    # For tracking advances/payments to specific staff
    staff_member = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='expenses'
    )
    
    # Receipt upload
    receipt = models.FileField(
        upload_to='receipts/', 
        null=True, 
        blank=True,
        help_text="Upload receipt (PDF, JPG, PNG)"
    )
    
    # Auditing
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-expense_date']

    def __str__(self):
        return f"{self.description} - {self.amount}"