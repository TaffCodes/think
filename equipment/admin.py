# equipment/admin.py
# (Edit this file)

from django.contrib import admin
from .models import (
    EquipmentCategory, EquipmentItem, 
    EquipmentRequest, RequestedItem, CheckoutLog
)

# ... (EquipmentCategoryAdmin, EquipmentItemAdmin, RequestedItemInline, EquipmentRequestAdmin, RequestedItemAdmin are unchanged) ...
@admin.register(EquipmentCategory)
class EquipmentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
@admin.register(EquipmentItem)
class EquipmentItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'total_quantity', 'available_quantity', 'get_damaged_quantity')
    list_filter = ('category',)
    search_fields = ('name',)
    readonly_fields = ('available_quantity', 'get_damaged_quantity')
class RequestedItemInline(admin.TabularInline):
    model = RequestedItem
    autocomplete_fields = ['item']
    extra = 1
@admin.register(EquipmentRequest)
class EquipmentRequestAdmin(admin.ModelAdmin):
    list_display = ('project', 'requested_by', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    autocomplete_fields = ['project', 'requested_by']
    inlines = [RequestedItemInline]
    date_hierarchy = 'created_at'
    search_fields = ('project__company_name', 'requested_by__username')
@admin.register(RequestedItem)
class RequestedItemAdmin(admin.ModelAdmin):
    list_display = ('request', 'item', 'quantity')
    autocomplete_fields = ['request', 'item']


# --- THIS REGISTRATION IS MODIFIED ---
@admin.register(CheckoutLog)
class CheckoutLogAdmin(admin.ModelAdmin):
    list_display = (
        'request', 
        'item',  # 'quantity' is removed
        'checked_out_by', 
        'checked_out_at', 
        'checked_in_by', 
        'checked_in_at', 
        'return_status'
    )
    list_filter = ('return_status', 'checked_out_at', 'checked_in_at')
    autocomplete_fields = ['request', 'item', 'checked_out_by', 'checked_in_by']
    search_fields = ('item__name', 'request__project__company_name')