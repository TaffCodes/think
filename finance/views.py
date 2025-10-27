# finance/views.py
# (Create this file)

from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Expense
from .forms import ExpenseForm

class ExpenseListView(LoginRequiredMixin, ListView):
    """
    Shows a list of all expenses.
    """
    model = Expense
    template_name = 'finance/expense_list.html'
    context_object_name = 'expenses'
    paginate_by = 20

    # In future, we can filter by department
    # def get_queryset(self):
    #     ...

class ExpenseCreateView(LoginRequiredMixin, CreateView):
    """
    A view with a form to create a new expense.
    """
    model = Expense
    form_class = ExpenseForm
    template_name = 'finance/expense_form.html'
    success_url = reverse_lazy('expense-list') # Redirect to list page on success

    def form_valid(self, form):
        """
        Assign the currently logged-in user as the 'added_by' user.
        """
        form.instance.added_by = self.request.user
        return super().form_valid(form)