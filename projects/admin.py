# projects/admin.py
# (Edit this file)

from django.contrib import admin
from .models import Service, Project, ProjectAllocation

class ProjectAllocationInline(admin.TabularInline):
    model = ProjectAllocation
    extra = 1 
    autocomplete_fields = ['user', 'allocated_by']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'date_from', 'date_to', 'status', 'charges', 'is_paid')
    list_filter = ('status', 'is_paid', 'date_from')
    search_fields = ('company_name', 'contact_person')
    filter_horizontal = ('services',) 
    inlines = [ProjectAllocationInline]
    
    def save_model(self, request, obj, form, change):
        if not obj.pk: 
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    # --- UPDATED ---
    list_display = ('name', 'department') # Show department in list
    search_fields = ('name',)
    list_filter = ('department',)         # Filter by department

@admin.register(ProjectAllocation)
class ProjectAllocationAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'allocated_at', 'allocated_by')
    list_filter = ('project', 'user')
    autocomplete_fields = ['project', 'user', 'allocated_by']