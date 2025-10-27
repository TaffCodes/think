# core/views.py
#
# This file contains the logic for our dashboard page

from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from users.models import UserProfile # We'll use this for verification

# We'll build on this view to check for verification
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'
    
    def get(self, request, *args, **kwargs):
        # Here we check if the user is verified
        # We can also check if the site settings have registrations open
        
        # In a future step, if 'is_verified' is false,
        # we can redirect them to a "Pending Verification" page.
        
        # For now, just show the dashboard.
        return super().get(request, *args, **kwargs)