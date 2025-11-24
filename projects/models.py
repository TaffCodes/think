# projects/models.py
# (Complete, Updated File)

from django.db import models
from django.contrib.auth.models import User, Group # <-- Import Group
from django.urls import reverse

class Service(models.Model):
    """
    Model to store the list of services offered.
    Now linked to a Department (Group) for financial attribution.
    """
    name = models.CharField(max_length=100, unique=True)
    
    # --- NEW FIELD ---
    # Link this service to a Department (Group)
    department = models.ForeignKey(
        Group, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="The department that owns this service (for revenue splits)."
    )
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Project(models.Model):
    STATUS_CHOICES = [
        ('UPCOMING', 'Upcoming'),
        ('STARTED', 'Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('PAUSED', 'Paused'),
        ('COMPLETED', 'Completed'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
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
    
    is_paid = models.BooleanField(default=False, help_text="Has the client payment been received?")
    
    # Optional description field if you added it earlier
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-date_from']

    def __str__(self):
        return f"{self.company_name} ({self.date_from.strftime('%d-%b-%Y')})"

    def get_absolute_url(self):
        return reverse('project-detail', args=[str(self.id)])


class ProjectAllocation(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='team')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='projects')
    allocated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='allocated_by')
    allocated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'user')

    def __str__(self):
        return f"{self.user.username} on {self.project.company_name}"