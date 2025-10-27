# equipment/views.py
# (Edit this file)

from django.views.generic import CreateView, ListView, DetailView, View, FormView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse, HttpResponseRedirect, Http404
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from .models import EquipmentRequest, RequestedItem, EquipmentItem, CheckoutLog
from .forms import (
    EquipmentRequestForm, RequestItemFormSet, 
    BaseCheckInFormSet # 1. Import new formset
)

# ... (StaffRequiredMixin, EquipmentRequestCreateView, RequestListView, RequestDetailView, ApproveRequestView, RejectRequestView are unchanged) ...
class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff
class EquipmentRequestCreateView(LoginRequiredMixin, CreateView):
    model = EquipmentRequest
    form_class = EquipmentRequestForm
    template_name = 'equipment/equipment_request_form.html'
    success_url = reverse_lazy('dashboard')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['item_formset'] = RequestItemFormSet(self.request.POST, prefix='items')
        else:
            context['item_formset'] = RequestItemFormSet(prefix='items')
        equipment_data = {item.pk: item.available_quantity for item in EquipmentItem.objects.filter(total_quantity__gt=0)}
        context['equipment_data_json'] = JsonResponse(equipment_data).content.decode('utf-8')
        return context
    def form_valid(self, form):
        context = self.get_context_data()
        item_formset = context['item_formset']
        with transaction.atomic():
            form.instance.requested_by = self.request.user
            self.object = form.save() 
            if item_formset.is_valid():
                item_formset.instance = self.object
                item_formset.save()
                messages.success(self.request, "Your equipment request has been submitted successfully.")
                return super().form_valid(form)
            else:
                return self.form_invalid(form)
    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        context = self.get_context_data()
        context['form'] = form
        if 'item_formset' not in context:
             context['item_formset'] = RequestItemFormSet(self.request.POST, prefix='items')
        return self.render_to_response(context)
class RequestListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = EquipmentRequest
    template_name = 'equipment/request_list.html'
    context_object_name = 'requests'
    paginate_by = 15
    ordering = ['-created_at']
    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset
class RequestDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    model = EquipmentRequest
    template_name = 'equipment/request_detail.html'
    context_object_name = 'request'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.all()
        context['logs'] = self.object.logs.filter(checked_in_at__isnull=True)
        return context
class ApproveRequestView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        req = get_object_or_404(EquipmentRequest, pk=self.kwargs.get('pk'))
        if req.status == 'PENDING':
            for item in req.items.all():
                if item.quantity > item.item.available_quantity:
                    messages.error(request, f"Cannot approve: Not enough stock for {item.item.name}. Only {item.item.available_quantity} available.")
                    return redirect('request-detail', pk=req.pk)
            req.status = 'APPROVED'
            req.save()
            messages.success(request, "Request has been approved.")
        else:
            messages.warning(request, "This request is not in a 'Pending' state.")
        return redirect('request-detail', pk=req.pk)
class RejectRequestView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        req = get_object_or_404(EquipmentRequest, pk=self.kwargs.get('pk'))
        if req.status == 'PENDING' or req.status == 'APPROVED':
            req.status = 'REJECTED'
            req.admin_notes = request.POST.get('admin_notes', 'No reason provided.')
            req.save()
            messages.success(request, "Request has been rejected.")
        else:
            messages.warning(request, "This request cannot be rejected.")
        return redirect('request-detail', pk=req.pk)


# --- THIS VIEW IS MODIFIED ---

class CheckoutView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    model = EquipmentRequest
    template_name = 'equipment/checkout_form.html'
    context_object_name = 'request'

    def get(self, request, *args, **kwargs):
        req = self.get_object()
        if req.status != 'APPROVED':
            messages.error(request, "This request must be approved before checkout.")
            return redirect('request-detail', pk=req.pk)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        req = self.get_object()
        if req.status != 'APPROVED':
            messages.error(request, "This request must be approved before checkout.")
            return redirect('request-detail', pk=req.pk)
        
        try:
            with transaction.atomic():
                # --- THIS IS THE NEW LOGIC ---
                # We create a list of log objects to be created
                logs_to_create = []
                for item in req.items.all():
                    # For each "RequestedItem" (e.g., 3 cameras)
                    # We create that many "CheckoutLog" entries
                    for _ in range(item.quantity):
                        logs_to_create.append(
                            CheckoutLog(
                                request=req,
                                item=item.item,
                                checked_out_by=request.user,
                                checked_out_at=timezone.now()
                            )
                        )
                
                # We create them all at once
                CheckoutLog.objects.bulk_create(logs_to_create)
                
                req.status = 'CHECKED_OUT'
                req.save()
            
            messages.success(request, f"Successfully checked out {len(logs_to_create)} items.")
            return redirect('request-detail', pk=req.pk)
        
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('request-detail', pk=req.pk)

# --- ADD THIS NEW VIEW ---

class CheckInView(LoginRequiredMixin, StaffRequiredMixin, FormView):
    """
    This view handles the check-in formset.
    """
    template_name = 'equipment/checkin_form.html'
    form_class = BaseCheckInFormSet # Use the formset as the base
    
    def get_queryset(self):
        """
        Define the queryset for the formset:
        Only get logs for this request that are NOT yet checked in.
        """
        # We store the request object on 'self' so we can access it later
        self.request_object = get_object_or_404(EquipmentRequest, pk=self.kwargs.get('pk'))
        
        if self.request_object.status not in ['CHECKED_OUT', 'PARTIAL_RETURN']:
             raise Http404("This request is not eligible for check-in.")
             
        return CheckoutLog.objects.filter(
            request=self.request_object,
            checked_in_at__isnull=True # Not yet returned
        ).order_by('item__name')

    def get_form_kwargs(self):
        """
        Pass the queryset to the formset.
        """
        kwargs = super().get_form_kwargs()
        kwargs['queryset'] = self.get_queryset()
        return kwargs

    def get_context_data(self, **kwargs):
        """
        Pass the request object to the template.
        """
        context = super().get_context_data(**kwargs)
        # Use the request_object we already fetched
        context['request'] = self.request_object
        return context

    def form_valid(self, formset):
        """
        This is called when the formset is submitted and valid.
        """
        
        # --- THIS IS THE FIX ---
        # Get the request object *before* we save the formset,
        # using the one we saved in get_queryset.
        request_obj = self.request_object
        # --- END OF FIX ---

        try:
            with transaction.atomic():
                instances = formset.save(commit=False)
                for log in instances:
                    # For each log being updated, set the check-in user and time
                    log.checked_in_by = self.request.user
                    log.checked_in_at = timezone.now()
                    log.save()
                
                # Now, update the main Request status
                
                # See if there are any *other* items still checked out
                still_out_count = CheckoutLog.objects.filter(
                    request=request_obj,
                    checked_in_at__isnull=True
                ).count()
                
                if still_out_count == 0:
                    request_obj.status = 'RETURNED'
                else:
                    request_obj.status = 'PARTIAL_RETURN'
                request_obj.save()

            messages.success(self.request, f"Successfully checked in {len(instances)} items.")
            return redirect('request-detail', pk=request_obj.pk)

        except Exception as e:
            # We add a print statement here to help debug if it happens again
            print(f"Error during check-in: {e}")
            messages.error(self.request, f"An error occurred during check-in: {e}")
            return self.form_invalid(formset)

    def form_invalid(self, formset):
        messages.error(self.request, "Please correct the errors below and set a status for all items.")
        return super().form_invalid(formset)