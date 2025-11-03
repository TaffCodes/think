# equipment/urls.py
# (Edit this file)

from django.urls import path
from .views import (
    EquipmentRequestCreateView,
    RequestListView,
    RequestDetailView,
    ApproveRequestView,
    RejectRequestView,
    CheckoutView,
    CheckInView,
    EquipmentListView,
    RepairListView,
    MarkAsRepairedView,
    DownloadCheckoutSheetView, # <-- ADD
    EmailCheckoutSheetView,    # <-- ADD
    PrintCheckoutSheetView,    # <-- ADD
    PrintToHpeprintView        # <-- ADD
)

urlpatterns = [
    path('', EquipmentListView.as_view(), name='equipment-list'),
    path('repair/', RepairListView.as_view(), name='repair-list'),
    path('repair/<int:pk>/mark/', MarkAsRepairedView.as_view(), name='mark-as-repaired'),

    # User-facing
    path('request/', EquipmentRequestCreateView.as_view(), name='equipment-request'),
    
    # Admin-facing
    path('requests/', RequestListView.as_view(), name='request-list'),
    path('requests/<int:pk>/', RequestDetailView.as_view(), name='request-detail'),
    path('requests/<int:pk>/approve/', ApproveRequestView.as_view(), name='request-approve'),
    path('requests/<int:pk>/reject/', RejectRequestView.as_view(), name='request-reject'),
    path('requests/<int:pk>/checkout/', CheckoutView.as_view(), name='request-checkout'),
    path('requests/<int:pk>/checkin/', CheckInView.as_view(), name='request-checkin'),
    
    # --- ADD THESE NEW URLS ---
    path('requests/<int:pk>/pdf/', DownloadCheckoutSheetView.as_view(), name='request-pdf'),
    path('requests/<int:pk>/print/', PrintCheckoutSheetView.as_view(), name='request-print'),
    path('requests/<int:pk>/email/', EmailCheckoutSheetView.as_view(), name='request-email'),
    path('requests/<int:pk>/hpeprint/', PrintToHpeprintView.as_view(), name='request-hpeprint'),
]