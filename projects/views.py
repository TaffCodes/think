# projects/views.py
# (Edit this file)

from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.db import IntegrityError # To catch errors
from .models import Project, ProjectAllocation
from .forms import ProjectForm, ProjectAllocationForm # 1. Import new form

class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 10

# --- MODIFY THIS VIEW CLASS ---

class ProjectDetailView(LoginRequiredMixin, DetailView):
    """
    Shows the full details for a single project.
    Also handles the POST request for adding a team member.
    """
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        """
        Add the allocation form to the context.
        """
        context = super().get_context_data(**kwargs)
        context['allocation_form'] = ProjectAllocationForm()
        # Also pass in the team members
        context['team'] = self.object.team.all()
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle the POST request to add a team member.
        """
        # Only allow Admins (staff) to do this
        if not request.user.is_staff:
            messages.error(request, "You do not have permission to add team members.")
            return redirect('project-detail', pk=self.get_object().pk)

        form = ProjectAllocationForm(request.POST)
        project = self.get_object()

        if form.is_valid():
            try:
                allocation = form.save(commit=False)
                allocation.project = project
                allocation.allocated_by = request.user
                allocation.save()
                messages.success(request, f"{allocation.user.username} has been added to the team.")
            except IntegrityError:
                # This catches the 'unique_together' error if user is already on team
                messages.warning(request, "This user is already on the team.")
        else:
            messages.error(request, "Invalid form submission. Please select a user.")
        
        return redirect('project-detail', pk=project.pk)


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    success_url = reverse_lazy('project-list') 

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)