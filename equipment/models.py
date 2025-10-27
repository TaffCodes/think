# equipment/models.py
# (This is the complete, up-to-date file)

from django.db import models
from django.db.models import Sum, Q
from projects.models import Project
from django.contrib.auth.models import User

class EquipmentCategory(models.Model):
    """
    Categories for equipment, e.g., "Cameras", "Audio", "Lighting".
    """
    name = models.CharField(max_length=100, unique=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Equipment categories"

    def __str__(self):
        return self.name

class EquipmentItem(models.Model):
    """
    The master list of a specific piece of equipment.
    """
    name = models.CharField(max_length=150)
    category = models.ForeignKey(
        EquipmentCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='items'
    )
    total_quantity = models.PositiveIntegerField(default=1)
    
    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} (Total: {self.total_quantity})"
    
    def get_committed_quantity(self):
        """
        Calculates the total quantity of this item that is currently
        committed (i.e., NOT available).
        This includes items on APPROVED, CHECKED_OUT, or PARTIAL_RETURN requests.
        PENDING requests do NOT reserve stock.
        """
        
        # 1. Count items on APPROVED requests (from RequestedItem)
        # These are items that are reserved but not yet physically checked out.
        approved_sum = RequestedItem.objects.filter(
            item=self,
            request__status='APPROVED'  # <-- PENDING is correctly removed
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        # 2. Count items that are CHECKED_OUT or PARTIALLY_RETURNED (from CheckoutLog)
        # These are items physically out of the building.
        # We only count logs that have NOT been checked in.
        checked_out_sum = CheckoutLog.objects.filter(
            item=self,
            request__status__in=['CHECKED_OUT', 'PARTIAL_RETURN'],
            checked_in_at__isnull=True # Not yet returned
        ).count() # .count() because each log is 1 item
        
        return approved_sum + checked_out_sum
    
    def get_damaged_quantity(self):
        """
        Calculates total quantity of this item marked as DAMAGED or LOST.
        These items are considered "out of circulation".
        """
        damaged_sum = CheckoutLog.objects.filter(
            item=self,
            return_status__in=['DAMAGED', 'LOST']
        ).count() # .count() because each log is 1 item
        return damaged_sum
        
    @property
    def available_quantity(self):
        """
        The actual available quantity: Total - Committed - Damaged.
        """
        return self.total_quantity - self.get_committed_quantity() - self.get_damaged_quantity()

class EquipmentRequest(models.Model):
    """
    The "header" for a request, linking a project and user.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('CHECKED_OUT', 'Checked Out'),
        ('PARTIAL_RETURN', 'Partially Returned'),
        ('RETURNED', 'Returned'),
    ]
    
    project = models.ForeignKey(
        Project, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='equipment_requests'
    )
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    
    admin_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        project_name = self.project.company_name if self.project else "No Project"
        return f"Request for {project_name} by {self.requested_by.username}"

class RequestedItem(models.Model):
    """
    A specific "line item" on an EquipmentRequest.
    e.g., 2 of "Sony A7S III"
    """
    request = models.ForeignKey(
        EquipmentRequest, 
        on_delete=models.CASCADE, 
        related_name='items'
    )
    item = models.ForeignKey(
        EquipmentItem, 
        on_delete=models.CASCADE, 
        related_name='requests'
    )
    quantity = models.PositiveIntegerField(default=1)
    
    class Meta:
        # A user can't add the same item twice to the same request
        unique_together = ('request', 'item')
    
    def __str__(self):
        return f"{self.quantity} of {self.item.name}"

class CheckoutLog(models.Model):
    """
    The master log. Each entry represents ONE single item.
    """
    RETURN_STATUS_CHOICES = [
        ('GOOD', 'Good'),
        ('DAMAGED', 'Damaged'),
        ('LOST', 'Lost'),
    ]

    request = models.ForeignKey(EquipmentRequest, on_delete=models.CASCADE, related_name='logs')
    item = models.ForeignKey(EquipmentItem, on_delete=models.PROTECT) # Don't delete item if it's in a log
    
    checked_out_by = models.ForeignKey(User, related_name='checked_out_by', on_delete=models.SET_NULL, null=True)
    checked_out_at = models.DateTimeField(auto_now_add=True)
    
    checked_in_by = models.ForeignKey(User, related_name='checked_in_by', on_delete=models.SET_NULL, null=True, blank=True)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    
    return_status = models.CharField(max_length=10, choices=RETURN_STATUS_CHOICES, null=True, blank=True)
    
    class Meta:
        ordering = ['-checked_out_at']

    def __str__(self):
        return f"1 of {self.item.name} for request {self.request.id}"