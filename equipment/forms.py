# equipment/forms.py
# (Edit this file)

from django import forms
from django.forms import inlineformset_factory, modelformset_factory
from .models import EquipmentRequest, RequestedItem, EquipmentItem, CheckoutLog
from projects.models import Project
from django.contrib.auth.models import User

# ... (EquipmentRequestForm, BaseRequestItemForm, RequestItemFormSet are unchanged) ...
class EquipmentRequestForm(forms.ModelForm):
    project = forms.ModelChoiceField(
        queryset=Project.objects.filter(status__in=['STARTED', 'IN_PROGRESS']),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Project"
    )
    class Meta:
        model = EquipmentRequest
        fields = ['project']

class BaseRequestItemForm(forms.ModelForm):
    item = forms.ModelChoiceField(
        queryset=EquipmentItem.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select item-select'})
    )
    quantity = forms.NumberInput(attrs={'class': 'form-control quantity-input', 'min': 1, 'value': 1})
    class Meta:
        model = RequestedItem
        fields = ['item', 'quantity']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['item'].queryset = EquipmentItem.objects.filter(total_quantity__gt=0)
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        item = self.cleaned_data.get('item')
        original_quantity = self.instance.quantity if self.instance.pk else 0
        
        if quantity and item:
            available_now = item.available_quantity + original_quantity
            if quantity > available_now:
                raise forms.ValidationError(
                    f"Not enough stock. Only {available_now} available, but {quantity} requested."
                )
        return quantity

RequestItemFormSet = inlineformset_factory(
    EquipmentRequest,
    RequestedItem,
    form=BaseRequestItemForm,
    extra=1,
    can_delete=True,
    can_delete_extra=True,
    min_num=1,
    validate_min=True,
)


# --- ADD THIS NEW FORM AND FORMSET ---

class CheckInLogForm(forms.ModelForm):
    """
    A form for a single CheckoutLog item, allowing an Admin
    to set the return_status.
    """
    # We make the status required for check-in
    return_status = forms.ChoiceField(
        choices=CheckoutLog.RETURN_STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    
    class Meta:
        model = CheckoutLog
        fields = ['return_status']

# This formset will manage all the CheckoutLog items for a request
BaseCheckInFormSet = modelformset_factory(
    CheckoutLog,
    form=CheckInLogForm,
    extra=0, # Don't show any extra forms, only existing ones
)

class EmailCheckoutSheetForm(forms.Form):
    """
    A simple form to select a user to email the checkout sheet to.
    """
    user_to_email = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True, email__isnull=False).exclude(email=''),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Select User to Email",
        help_text="Select a staff member to send the checkout sheet to."
    )