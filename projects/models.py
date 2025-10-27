# projects/models.py
# (Create this file)

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Service(models.Model):
    """
    Model to store the list of services offered (e.g., sound, videography).
    """
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Project(models.Model):
    """
    The main model for capturing a project.
    """
    STATUS_CHOICES = [
        ('STARTED', 'Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('PAUSED', 'Paused'),
        ('COMPLETED', 'Completed'),
        ('DELIVERED', 'Delivered'),
    ]

    company_name = models.CharField(max_length=200)
    services = models.ManyToManyField(Service, help_text="Select services required for this project")
    date_from = models.DateField()
    date_to = models.DateField()
    location = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=100)
    charges = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='STARTED')
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_projects')

    class Meta:
        ordering = ['-date_from'] # Show newest projects first

    def __str__(self):
        return f"{self.company_name} ({self.date_from.strftime('%d-%b-%Y')})"

    def get_absolute_url(self):
        """
        Returns the URL for this specific project instance.
        """
        return reverse('project-detail', args=[str(self.id)])


class ProjectAllocation(models.Model):
    """
    Model to allocate users (staff) to a specific project.
    This is the "through" model for tracking who worked on what.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='team')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='projects')
    allocated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='allocated_by')
    allocated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'user') # A user can only be on a project once

    def __str__(self):
        return f"{self.user.username} on {self.project.company_name}"