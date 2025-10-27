# projects/admin.py
# (Create this file)

from django.contrib import admin
from .models import Service, Project, ProjectAllocation

class ProjectAllocationInline(admin.TabularInline):
    """
    Allows adding team members directly from the Project admin page.
    """
    model = ProjectAllocation
    extra = 1 # Show one extra blank slot
    autocomplete_fields = ['user', 'allocated_by']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'date_from', 'date_to', 'status', 'charges', 'created_by')
    list_filter = ('status', 'services', 'date_from')
    search_fields = ('company_name', 'contact_person')
    filter_horizontal = ('services',) # Makes ManyToMany field user-friendly
    inlines = [ProjectAllocationInline]
    
    def save_model(self, request, obj, form, change):
        if not obj.pk: # If this is a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(ProjectAllocation)
class ProjectAllocationAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'allocated_at', 'allocated_by')
    list_filter = ('project', 'user')
    autocomplete_fields = ['project', 'user', 'allocated_by']