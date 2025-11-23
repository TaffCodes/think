from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import EquipmentItem, EquipmentRequest, RequestedItem, CheckoutLog
from .serializers import (
    EquipmentItemSerializer, EquipmentRequestSerializer, CheckoutLogSerializer
)
from .views import PrintToHpeprintView # Reusing email logic if possible, or replicate

class EquipmentItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EquipmentItem.objects.all()
    serializer_class = EquipmentItemSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['category']
    search_fields = ['name']

class CheckoutLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Used for the Repair Center (listing damaged items).
    """
    queryset = CheckoutLog.objects.filter(return_status__in=['DAMAGED', 'LOST'])
    serializer_class = CheckoutLogSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=['post'])
    def repair(self, request, pk=None):
        log = self.get_object()
        log.delete() # Logic: Deleting the log returns item to inventory
        return Response({'status': 'Item marked as repaired'})

class EquipmentRequestViewSet(viewsets.ModelViewSet):
    queryset = EquipmentRequest.objects.all().order_by('-created_at')
    serializer_class = EquipmentRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users only see their own requests unless they are staff
        user = self.request.user
        if user.is_staff:
            return EquipmentRequest.objects.all().order_by('-created_at')
        return EquipmentRequest.objects.filter(requested_by=user).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        # Custom create to handle nested items
        project_id = request.data.get('project')
        items_data = request.data.get('items', []) # List of {item_id, quantity}

        if not items_data:
            return Response({'error': 'No items provided'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            req_obj = EquipmentRequest.objects.create(
                project_id=project_id,
                requested_by=request.user,
                status='PENDING'
            )
            
            # Validate stock and create items
            for item_data in items_data:
                item_id = item_data.get('item_id')
                qty = int(item_data.get('quantity', 1))
                equipment = get_object_or_404(EquipmentItem, pk=item_id)
                
                # Check stock
                if qty > equipment.available_quantity:
                    transaction.set_rollback(True)
                    return Response(
                        {'error': f'Not enough stock for {equipment.name}. Available: {equipment.available_quantity}'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                RequestedItem.objects.create(request=req_obj, item=equipment, quantity=qty)

        serializer = self.get_serializer(req_obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        req = self.get_object()
        # Re-check stock
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
        req.admin_notes = request.data.get('reason', '')
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
        """
        Payload: { "items": [ { "log_id": 1, "status": "GOOD" }, ... ] }
        """
        req = self.get_object()
        items_data = request.data.get('items', [])
        
        for item_data in items_data:
            log = get_object_or_404(CheckoutLog, pk=item_data['log_id'])
            log.return_status = item_data['status']
            log.checked_in_by = request.user
            log.checked_in_at = timezone.now()
            log.save()
            
        # Update main status logic (simplified)
        if not req.logs.filter(checked_in_at__isnull=True).exists():
            req.status = 'RETURNED'
        else:
            req.status = 'PARTIAL_RETURN'
        req.save()
        
        return Response({'status': 'Checked In'})