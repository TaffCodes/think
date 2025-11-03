# equipment/views.py
# (This is the complete, updated file)

from django.views.generic import CreateView, ListView, DetailView, View, FormView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db import transaction
# --- We need HttpResponseRedirect for the new logic ---
from django.http import JsonResponse, HttpResponseRedirect, Http404
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from .models import EquipmentRequest, RequestedItem, EquipmentItem, CheckoutLog
from .forms import (
    EquipmentRequestForm, RequestItemFormSet, 
    BaseCheckInFormSet, EmailCheckoutSheetForm
)
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from weasyprint import HTML, CSS
from django.conf import settings
import os


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff
    
class EquipmentListView(LoginRequiredMixin, ListView):
    """
    Main dashboard for the equipment module.
    Shows a complete list of all inventory items.
    """
    model = EquipmentItem
    template_name = 'equipment/equipment_list.html'
    context_object_name = 'items'
    paginate_by = 20

    def get_queryset(self):
        # Allow searching by name
        queryset = super().get_queryset().order_by('category', 'name')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

# --- THIS VIEW IS MODIFIED ---
class EquipmentRequestCreateView(LoginRequiredMixin, CreateView):
    model = EquipmentRequest
    form_class = EquipmentRequestForm
    template_name = 'equipment/equipment_request_form.html'
    success_url = reverse_lazy('dashboard')

    def get_context_data(self, **kwargs):
        """
        Add the item_formset to the context.
        """
        context = super().get_context_data(**kwargs)
        
        if self.request.POST:
            # --- MODIFICATION ---
            # If we are being re-rendered by form_invalid,
            # we need to use the invalid formset we already processed
            # to make sure its errors are displayed.
            if hasattr(self, 'invalid_formset'):
                context['item_formset'] = self.invalid_formset
            else:
                context['item_formset'] = RequestItemFormSet(self.request.POST, prefix='items')
        else:
            context['item_formset'] = RequestItemFormSet(prefix='items')
        
        equipment_data = {
            item.pk: item.available_quantity 
            for item in EquipmentItem.objects.filter(total_quantity__gt=0)
        }
        context['equipment_data_json'] = JsonResponse(equipment_data).content.decode('utf-8')
        return context

    def form_valid(self, form):
        """
        This method is called when the main form (EquipmentRequestForm) is valid.
        We now validate the formset *before* saving anything.
        """
        context = self.get_context_data()
        item_formset = context['item_formset']
        
        if item_formset.is_valid():
            # Formset is also valid, proceed to save everything
            with transaction.atomic():
                form.instance.requested_by = self.request.user
                self.object = form.save() 
                
                item_formset.instance = self.object
                item_formset.save()
            
            messages.success(self.request, "Your equipment request has been submitted successfully.")
            # We must return a redirect here
            return HttpResponseRedirect(self.get_success_url())
        else:
            # --- THIS IS THE FIX ---
            # The formset is invalid. We store it on 'self'
            # so get_context_data can retrieve it, and then
            # we call form_invalid.
            # NO record is saved to the database.
            self.invalid_formset = item_formset
            return self.form_invalid(form)

    def form_invalid(self, form):
        """
        This method is called if the main form is invalid,
        OR if we call it manually from form_valid (when the formset is invalid).
        """
        messages.error(self.request, "Please correct the errors below.")
        
        # --- MODIFICATION ---
        # We now just render the context, which get_context_data()
        # will correctly populate with the invalid form and formset,
        # preserving all the user's data and error messages.
        return self.render_to_response(self.get_context_data(form=form))


# --- ALL OTHER VIEWS ARE UNCHANGED ---

class RequestListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    # ... (no changes) ...
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
    # ... (no changes) ...
    model = EquipmentRequest
    template_name = 'equipment/request_detail.html'
    context_object_name = 'request'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.all()
        context['logs'] = self.object.logs.filter(checked_in_at__isnull=True)
        return context

class ApproveRequestView(LoginRequiredMixin, StaffRequiredMixin, View):
    # ... (no changes) ...
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
    # ... (no changes) ...
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

class CheckoutView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    # ... (no changes) ...
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
                logs_to_create = []
                for item in req.items.all():
                    for _ in range(item.quantity):
                        logs_to_create.append(
                            CheckoutLog(
                                request=req,
                                item=item.item,
                                checked_out_by=request.user,
                                checked_out_at=timezone.now()
                            )
                        )
                CheckoutLog.objects.bulk_create(logs_to_create)
                req.status = 'CHECKED_OUT'
                req.save()
            messages.success(request, f"Successfully checked out {len(logs_to_create)} items.")
            return redirect('request-detail', pk=req.pk)
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('request-detail', pk=req.pk)

class CheckInView(LoginRequiredMixin, StaffRequiredMixin, FormView):
    # ... (no changes) ...
    template_name = 'equipment/checkin_form.html'
    form_class = BaseCheckInFormSet
    def get_queryset(self):
        self.request_object = get_object_or_404(EquipmentRequest, pk=self.kwargs.get('pk'))
        if self.request_object.status not in ['CHECKED_OUT', 'PARTIAL_RETURN']:
             raise Http404("This request is not eligible for check-in.")
        return CheckoutLog.objects.filter(
            request=self.request_object,
            checked_in_at__isnull=True
        ).order_by('item__name')
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['queryset'] = self.get_queryset()
        return kwargs
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['request'] = self.request_object
        return context
    def form_valid(self, formset):
        request_obj = self.request_object
        try:
            with transaction.atomic():
                instances = formset.save(commit=False)
                for log in instances:
                    log.checked_in_by = self.request.user
                    log.checked_in_at = timezone.now()
                    log.save()
                
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
            print(f"Error during check-in: {e}")
            messages.error(self.request, f"An error occurred during check-in: {e}")
            return self.form_invalid(formset)
    def form_invalid(self, formset):
        messages.error(self.request, "Please correct the errors below and set a status for all items.")
        return super().form_invalid(formset)

class RepairListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    """
    Displays a list of all equipment currently marked as 'Damaged' or 'Lost'.
    """
    model = CheckoutLog
    template_name = 'equipment/repair_list.html'
    context_object_name = 'damaged_items'
    paginate_by = 20
    
    def get_queryset(self):
        # Find all CheckoutLog entries that are marked as Damaged or Lost
        # and have NOT been deleted (which is our "repaired" state).
        return CheckoutLog.objects.filter(
            return_status__in=['DAMAGED', 'LOST']
        ).order_by('checked_in_at')

class MarkAsRepairedView(LoginRequiredMixin, StaffRequiredMixin, View):
    """
    Handles the 'POST' request to mark an item as repaired.
    Our repair logic is simple: we just delete the CheckoutLog entry
    that marked the item as damaged.
    """
    
    def post(self, request, *args, **kwargs):
        # Get the specific log entry for the damaged item
        log_pk = self.kwargs.get('pk')
        log = get_object_or_404(CheckoutLog, pk=log_pk)
        
        item_name = log.item.name
        
        # Deleting the log removes it from the 'get_damaged_quantity' count
        log.delete()
        
        messages.success(request, f"'{item_name}' has been marked as repaired and returned to the inventory.")
        return redirect('repair-list')
    
class DownloadCheckoutSheetView(LoginRequiredMixin, StaffRequiredMixin, View):
    """
    Generates and serves a PDF of the checkout sheet.
    """
    def get(self, request, *args, **kwargs):
        req = get_object_or_404(EquipmentRequest, pk=self.kwargs.get('pk'))
        
        # 1. Render the HTML template
        html_string = render_to_string('equipment/checkout_sheet.html', {'request': req})
        
        # 2. Use WeasyPrint to create the PDF in memory
        pdf_file = HTML(string=html_string).write_pdf()
        
        # 3. Create an HTTP response with the PDF
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="checkout_request_{req.pk}.pdf"'
        return response

class PrintCheckoutSheetView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    """
    Shows a simple, printable version of the checkout sheet.
    """
    model = EquipmentRequest
    template_name = 'equipment/checkout_sheet.html'
    context_object_name = 'request'

class EmailCheckoutSheetView(LoginRequiredMixin, StaffRequiredMixin, FormView):
    """
    Displays a form to select a user, then emails the PDF.
    """
    form_class = EmailCheckoutSheetForm
    template_name = 'equipment/email_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.request_object = get_object_or_404(EquipmentRequest, pk=self.kwargs.get('pk'))
        context['request'] = self.request_object
        return context

    def form_valid(self, form):
        user_to_email = form.cleaned_data['user_to_email']
        req = get_object_or_404(EquipmentRequest, pk=self.kwargs.get('pk'))
        
        try:
            # 1. Generate the PDF in memory
            html_string = render_to_string('equipment/checkout_sheet.html', {'request': req})
            pdf_file = HTML(string=html_string).write_pdf()
            pdf_filename = f'checkout_request_{req.pk}.pdf'

            # 2. Render the email body
            email_body = render_to_string('equipment/email/checkout_sheet_email.txt', {
                'request': req,
                'user': user_to_email
            })

            # 3. Create the email
            email = EmailMessage(
                subject=f"FikiriERP: Equipment Checkout Sheet for Request #{req.pk}",
                body=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[
                    user_to_email.email,        # The selected user
                    '73f38dyq@hpeprint.com'     # The HP ePrint email
                ],
                # cc=[self.request.user.email]  # Optionally CC the admin
            )

            # 4. Attach the PDF
            email.attach(pdf_filename, pdf_file, 'application/pdf')

            # 5. Send the email
            email.send()

            messages.success(self.request, f"Checkout sheet has been emailed to {user_to_email.email} and HP ePrint.")
            return redirect('request-detail', pk=req.pk)

        except Exception as e:
            messages.error(self.request, f"An error occurred while sending the email: {e}")
            return self.form_invalid(form)
        
class PrintToHpeprintView(LoginRequiredMixin, StaffRequiredMixin, View):
    """
    Handles a one-click action to send the PDF directly
    to the HP ePrint email address.
    """
    def post(self, request, *args, **kwargs):
        req = get_object_or_404(EquipmentRequest, pk=self.kwargs.get('pk'))
        
        try:
            # 1. Generate the PDF in memory
            html_string = render_to_string('equipment/checkout_sheet.html', {'request': req})
            pdf_file = HTML(string=html_string).write_pdf()
            pdf_filename = f'checkout_request_{req.pk}.pdf'

            # 2. Render a simple email body
            email_body = f"Please print the attached checkout sheet for Request #{req.pk}."

            # 3. Create the email
            email = EmailMessage(
                subject=f"PRINT: Equipment Checkout Sheet #{req.pk}",
                # body=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.PRINTER_EMAIL], # Send *only* to the printer
            )

            # 4. Attach the PDF
            email.attach(pdf_filename, pdf_file, 'application/pdf')

            # 5. Send the email
            email.send()

            messages.success(request, "The checkout sheet has been sent to the printer.")
        
        except Exception as e:
            messages.error(request, f"An error occurred while sending to printer: {e}")
            
        return redirect('request-detail', pk=req.pk)