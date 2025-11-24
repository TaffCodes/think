from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from weasyprint import HTML

from .models import EquipmentItem, EquipmentRequest, RequestedItem, CheckoutLog
from .serializers import EquipmentItemSerializer, EquipmentRequestSerializer, CheckoutLogSerializer

class EquipmentItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EquipmentItem.objects.all()
    serializer_class = EquipmentItemSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['category']
    search_fields = ['name']

class RepairLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CheckoutLog.objects.filter(return_status__in=['DAMAGED', 'LOST'])
    serializer_class = CheckoutLogSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=['post'])
    def repair(self, request, pk=None):
        log = self.get_object()
        log.delete() 
        return Response({'status': 'Item repaired'})

class EquipmentRequestViewSet(viewsets.ModelViewSet):
    queryset = EquipmentRequest.objects.all().order_by('-created_at')
    serializer_class = EquipmentRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return EquipmentRequest.objects.all().order_by('-created_at')
        return EquipmentRequest.objects.filter(requested_by=user).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        project_id = request.data.get('project_id')
        items_data = request.data.get('items', [])

        if not items_data:
            return Response({'error': 'No items provided'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            req_obj = EquipmentRequest.objects.create(
                project_id=project_id,
                requested_by=request.user,
                status='PENDING'
            )
            
            for item_data in items_data:
                item_id = item_data.get('item_id')
                qty = int(item_data.get('quantity', 1))
                equipment = get_object_or_404(EquipmentItem, pk=item_id)
                
                if qty > equipment.available_quantity:
                    transaction.set_rollback(True)
                    return Response(
                        {'error': f'Not enough stock for {equipment.name}. Available: {equipment.available_quantity}'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                RequestedItem.objects.create(request=req_obj, item=equipment, quantity=qty)

        return Response(self.get_serializer(req_obj).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        req = self.get_object()
        for item in req.items.all():
            if item.quantity > item.item.available_quantity:
                return Response({'error': f'Not enough stock for {item.item.name}'}, status=400)
        req.status = 'APPROVED'
        req.save()
        return Response({'status': 'Approved'})

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reject(self, request, pk=None):
        req = self.get_object()
        req.status = 'REJECTED'
        req.save()
        return Response({'status': 'Rejected'})

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def checkout(self, request, pk=None):
        req = self.get_object()
        if req.status != 'APPROVED':
            return Response({'error': 'Request must be approved first'}, status=400)
        
        logs = []
        for item in req.items.all():
            for _ in range(item.quantity):
                logs.append(CheckoutLog(
                    request=req, item=item.item, 
                    checked_out_by=request.user, 
                    checked_out_at=timezone.now()
                ))
        CheckoutLog.objects.bulk_create(logs)
        req.status = 'CHECKED_OUT'
        req.save()
        return Response({'status': 'Checked Out'})

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def checkin(self, request, pk=None):
        req = self.get_object()
        items_data = request.data.get('items', []) 
        
        for item_data in items_data:
            log = get_object_or_404(CheckoutLog, pk=item_data['log_id'])
            log.return_status = item_data['status']
            log.checked_in_by = request.user
            log.checked_in_at = timezone.now()
            log.save()
            
        if not req.logs.filter(checked_in_at__isnull=True).exists():
            req.status = 'RETURNED'
        else:
            req.status = 'PARTIAL_RETURN'
        req.save()
        return Response({'status': 'Checked In'})

    # --- NEW ACTIONS FOR PDF / PRINT / EMAIL ---

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def pdf(self, request, pk=None):
        """
        Generate and return the PDF file directly.
        URL: /api/v1/equipment/requests/{pk}/pdf/
        """
        req = self.get_object()
        try:
            html_string = render_to_string('equipment/checkout_sheet.html', {'request': req})
            pdf_file = HTML(string=html_string).write_pdf()
            response = HttpResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="checkout_request_{req.pk}.pdf"'
            return response
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    @action(detail=True, methods=['get'], url_path='print', permission_classes=[IsAuthenticated])
    def print_view(self, request, pk=None):
        """
        Render the HTML for browser printing.
        URL: /api/v1/equipment/requests/{pk}/print/
        """
        req = self.get_object()
        return render(request, 'equipment/checkout_sheet.html', {'request': req})

    @action(detail=True, methods=['post'], url_path='email', permission_classes=[IsAdminUser])
    def email_pdf(self, request, pk=None):
        """
        Email PDF to a specific user.
        URL: /api/v1/equipment/requests/{pk}/email/
        """
        req = self.get_object()
        user_email = request.data.get('user_email')
        
        try:
            html_string = render_to_string('equipment/checkout_sheet.html', {'request': req})
            pdf_file = HTML(string=html_string).write_pdf()
            
            email = EmailMessage(
                subject=f"Checkout Sheet #{req.pk}",
                body="Attached is the checkout sheet.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=['73f38dyq@hpeprint.com']
            )
            if user_email:
                email.to.append(user_email)
                
            email.attach(f'checkout_{req.pk}.pdf', pdf_file, 'application/pdf')
            email.send()
            return Response({'status': 'Email sent'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    @action(detail=True, methods=['post'], url_path='hpeprint', permission_classes=[IsAdminUser])
    def hpeprint(self, request, pk=None):
        """
        One-click send to HP Printer.
        URL: /api/v1/equipment/requests/{pk}/hpeprint/
        """
        req = self.get_object()
        try:
            html_string = render_to_string('equipment/checkout_sheet.html', {'request': req})
            pdf_file = HTML(string=html_string).write_pdf()
            
            email = EmailMessage(
                subject=f"PRINT: Request #{req.pk}",
                body="Auto-print request.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=['73f38dyq@hpeprint.com']
            )
            email.attach(f'checkout_{req.pk}.pdf', pdf_file, 'application/pdf')
            email.send()
            return Response({'status': 'Sent to printer'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)