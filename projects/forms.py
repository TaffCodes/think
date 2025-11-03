# projects/forms.py
# (This is the complete, up-to-date file)

from django import forms
from django.contrib.auth.models import User
from .models import Project, ProjectAllocation, Service

class ProjectForm(forms.ModelForm):
    """
    Form for creating new projects.
    """
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    
    class Meta:
        model = Project
        fields = [
            'company_name', 'services', 'date_from', 'date_to', 
            'location', 'contact_person', 'charges', 'status'
        ]
        
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_from': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_to': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'charges': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        
    def __init__(self, *args, **kwargs):
        """
        Add MDB 'form-outline' and 'mb-4' to all fields.
        """
        super().__init__(*args, **kwargs)
        
        non_checkbox_fields = [f for f in self.fields if f != 'services']
        
        for field_name in non_checkbox_fields:
            self.fields[field_name].widget.attrs.update({
                'class': self.fields[field_name].widget.attrs.get('class', '') + ' form-control-lg'
            })
            
        self.fields['services'].widget.attrs.update({'class': 'form-check-input'})

class ProjectAllocationForm(forms.ModelForm):
    """
    Form for allocating a user to a project.
    """
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select form-select-lg'})
    )

    class Meta:
        model = ProjectAllocation
        fields = ['user']

class UpdateProjectStatusForm(forms.ModelForm):
    """
    A simple form to update only the status of a project.
    """
    class Meta:
        model = Project
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'})
        }