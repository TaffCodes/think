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
    CheckInView,  # 1. Import new view
)

urlpatterns = [
    # User-facing
    path('request/', EquipmentRequestCreateView.as_view(), name='equipment-request'),
    
    # Admin-facing
    path('requests/', RequestListView.as_view(), name='request-list'),
    path('requests/<int:pk>/', RequestDetailView.as_view(), name='request-detail'),
    path('requests/<int:pk>/approve/', ApproveRequestView.as_view(), name='request-approve'),
    path('requests/<int:pk>/reject/', RejectRequestView.as_view(), name='request-reject'),
    path('requests/<int:pk>/checkout/', CheckoutView.as_view(), name='request-checkout'),
    path('requests/<int:pk>/checkin/', CheckInView.as_view(), name='request-checkin'), # 2. Add new URL
]