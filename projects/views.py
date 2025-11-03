# projects/views.py
# (This is the complete, up-to-date file)

from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Sum
from .models import Project, ProjectAllocation, Service
# Import all the forms
from .forms import ProjectForm, ProjectAllocationForm, UpdateProjectStatusForm
from decimal import Decimal

class ProjectListView(LoginRequiredMixin, ListView):
    """
    Shows a list of all projects, now with filtering.
    """
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 10

    def get_queryset(self):
        """
        Filter the queryset based on the 'service' GET parameter.
        """
        queryset = super().get_queryset().prefetch_related('services')
        service_id = self.request.GET.get('service')
        
        if service_id:
            queryset = queryset.filter(services__id=service_id)
            
        return queryset

    def get_context_data(self, **kwargs):
        """
        Pass the list of services to the template for the filter dropdown.
        """
        context = super().get_context_data(**kwargs)
        context['services_list'] = Service.objects.all()
        # Ensure selected_service is a string for comparison in the template
        context['selected_service'] = str(self.request.GET.get('service', ''))
        return context

class ProjectDetailView(LoginRequiredMixin, DetailView):
    """
    MODIFIED: This view now handles GET, and POST for two
    different forms (Team Allocation and Status Update).
    """
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        """
        Add all related data (team, equipment, finance) to the context.
        """
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        
        # 1. Team Allocation
        context['allocation_form'] = ProjectAllocationForm()
        context['team'] = project.team.all().select_related('user')
        
        # 2. Equipment Requests
        # We prefetch related items to avoid extra database queries
        context['equipment_requests'] = project.equipment_requests.all().order_by('-created_at')
        
        # 3. Financials
        # We prefetch related expenses
        expenses = project.expenses.all()
        total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        profit = project.charges - total_expenses
        
        context['expenses'] = expenses
        context['total_expenses'] = total_expenses
        context['profit'] = profit

        # 4. Status Update Form
        # We pass an 'instance' so it shows the project's current status
        context['status_form'] = UpdateProjectStatusForm(instance=project)
        
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests for both team allocation and status updates.
        """
        project = self.get_object()
        
        # Check for staff permissions
        if not request.user.is_staff:
            messages.error(request, "You do not have permission to perform this action.")
            return redirect('project-detail', pk=project.pk)
        
        # Get the 'action' from the hidden input in the form
        action = request.POST.get('action')

        if action == 'allocate_team':
            form = ProjectAllocationForm(request.POST)
            if form.is_valid():
                try:
                    allocation = form.save(commit=False)
                    allocation.project = project
                    allocation.allocated_by = request.user
                    allocation.save()
                    messages.success(request, f"{allocation.user.username} has been added to the team.")
                except IntegrityError:
                    messages.warning(request, "This user is already on the team.")
            else:
                messages.error(request, "Invalid team form submission. Please select a user.")
        
        elif action == 'update_status':
            # We pass 'instance=project' to update the existing project
            form = UpdateProjectStatusForm(request.POST, instance=project)
            if form.is_valid():
                form.save()
                messages.success(request, "Project status has been updated.")
            else:
                messages.error(request, "Invalid status form submission.")
        
        else:
            messages.error(request, "Unknown or missing action.")

        return redirect('project-detail', pk=project.pk)


class ProjectCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating a new project.
    """
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    success_url = reverse_lazy('project-list') 

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)