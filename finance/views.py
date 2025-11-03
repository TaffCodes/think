# finance/views.py
# (Edit this file)

from django.views.generic import ListView, CreateView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.contrib import messages
from .models import Expense, Transaction, Account
from .forms import ExpenseForm, TransactionForm, ProjectPaymentForm
from projects.models import Project, Service
from decimal import Decimal

# --- NEW VIEW ---
class AccountListView(LoginRequiredMixin, ListView):
    """
    Main dashboard for the finance module.
    Shows a list of all accounts and their balances.
    """
    model = Account
    template_name = 'finance/account_list.html'
    context_object_name = 'accounts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # We'll also show the 5 most recent transactions
        context['recent_transactions'] = Transaction.objects.all()[:5]
        return context

class ExpenseListView(LoginRequiredMixin, ListView):
    # ... (this view is unchanged) ...
    model = Expense
    template_name = 'finance/expense_list.html'
    context_object_name = 'expenses'
    paginate_by = 20

class ExpenseCreateView(LoginRequiredMixin, CreateView):
    # ... (this view is unchanged) ...
    model = Expense
    form_class = ExpenseForm
    template_name = 'finance/expense_form.html'
    success_url = reverse_lazy('expense-list')
    def form_valid(self, form):
        try:
            with transaction.atomic():
                form.instance.added_by = self.request.user
                expense = form.save()
                Transaction.objects.create(
                    amount=expense.amount,
                    description=f"Expense: {expense.description}",
                    from_account=expense.account,
                    to_account=None,
                    expense=expense,
                    project=expense.project
                )
                messages.success(self.request, "Expense recorded successfully.")
                return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f"An error occurred: {e}")
            return self.form_invalid(form)


# --- NEW VIEW ---
class TransactionCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    A view for Admins to create manual transactions
    (e.g., funding accounts, transfers).
    """
    model = Transaction
    form_class = TransactionForm
    template_name = 'finance/transaction_form.html'
    success_url = reverse_lazy('account-list')

    def test_func(self):
        # Only staff can make manual transactions
        return self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, "Transaction created successfully.")
        return super().form_valid(form)

# --- NEW VIEW ---
class ProjectPaymentView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    """
    This view handles receiving a project payment and splitting the funds.
    """
    form_class = ProjectPaymentForm
    template_name = 'finance/project_payment_form.html'
    success_url = reverse_lazy('account-list')

    def test_func(self):
        return self.request.user.is_staff
    
    def form_valid(self, form):
        project = form.cleaned_data['project']
        total_charges = project.charges
        
        try:
            with transaction.atomic():
                # 1. Get all the required accounts
                main_account = Account.objects.get(name__iexact="Main Account")
                logistics_account = Account.objects.get(name__iexact="Logistics")
                admin_account = Account.objects.get(name__iexact="Admin")
                
                # 2. Mark project as paid
                project.is_paid = True
                project.save()
                
                # 3. Create the main "credit" transaction
                Transaction.objects.create(
                    amount=total_charges,
                    description=f"Payment for project: {project.company_name}",
                    from_account=None, # From client
                    to_account=main_account,
                    project=project
                )
                
                # 4. Calculate and create the split "debit" transactions
                
                # 10% to Logistics
                logistics_cut = total_charges * Decimal('0.10')
                Transaction.objects.create(
                    amount=logistics_cut,
                    description=f"Logistics split for {project.company_name}",
                    from_account=main_account,
                    to_account=logistics_account,
                    project=project
                )
                
                # 15% to Admin
                admin_cut = total_charges * Decimal('0.15')
                Transaction.objects.create(
                    amount=admin_cut,
                    description=f"Admin split for {project.company_name}",
                    from_account=main_account,
                    to_account=admin_account,
                    project=project
                )
                
                # 35% split among engaged departments
                dept_cut_total = total_charges * Decimal('0.35')
                
                # Find the departments involved from the project's services
                # This assumes your Service names match your Account names (e.g., "Sound", "Visual")
                involved_depts_names = project.services.values_list('name', flat=True)
                
                # Get the Account objects for these departments
                # We filter for names that are *in* the services list
                involved_dept_accounts = Account.objects.filter(
                    name__in=involved_depts_names
                )
                
                if involved_dept_accounts.exists():
                    # Split the 35% cut equally among them
                    split_per_dept = dept_cut_total / involved_dept_accounts.count()
                    for dept_account in involved_dept_accounts:
                        Transaction.objects.create(
                            amount=split_per_dept,
                            description=f"Dept split for {project.company_name}",
                            from_account=main_account,
                            to_account=dept_account,
                            project=project
                        )
                
                # The remaining 40% (100 - 10 - 15 - 35) stays in the Main Account
                
                messages.success(self.request, f"Payment for '{project.company_name}' received and funds distributed.")
                return super().form_valid(form)

        except Account.DoesNotExist as e:
            messages.error(self.request, f"Error: Missing a required account ({e}). Please create 'Main Account', 'Logistics', and 'Admin' accounts.")
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f"An unexpected error occurred: {e}")
            return self.form_invalid(form)