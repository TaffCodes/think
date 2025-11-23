# fikirierp/urls.py
# (Edit this file)

from django.contrib import admin
from django.urls import path, include

# --- ADD THESE IMPORTS ---
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('projects/', include('projects.urls')),
    path('equipment/', include('equipment.urls')),
    path('finance/', include('finance.urls')),  # <-- ADD THIS LINE
    path('', include('core.urls')),

    # API Authentication (Login, Logout, Google)
    # This creates /api/login/, /api/logout/, /api/google/, etc.
    path('api-auth/', include('dj_rest_auth.urls')),
    
    # This is for Google Auth (if you set it up)
    path('api-auth/registration/', include('dj_rest_auth.registration.urls')),
]

# --- ADD THIS AT THE BOTTOM ---
# This is required to serve user-uploaded files (like receipts) during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#*********************************#
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import ViewSets
from users.api_views import UserViewSet
from projects.api_views import ProjectViewSet, ServiceViewSet
from equipment.api_views import (
    EquipmentItemViewSet, EquipmentRequestViewSet, CheckoutLogViewSet
)
from finance.api_views import (
    AccountViewSet, ExpenseViewSet, TransactionViewSet
)

# Create Router
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'equipment/items', EquipmentItemViewSet)
router.register(r'equipment/requests', EquipmentRequestViewSet)
router.register(r'equipment/repair-log', CheckoutLogViewSet)
router.register(r'finance/accounts', AccountViewSet)
router.register(r'finance/expenses', ExpenseViewSet)
router.register(r'finance/transactions', TransactionViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    
    # Original HTML Views
    path('projects/', include('projects.urls')),
    path('equipment/', include('equipment.urls')),
    path('finance/', include('finance.urls')),
    path('', include('core.urls')),

    # API Auth
    path('api/v1/auth/', include('dj_rest_auth.urls')),
    path('api/v1/auth/registration/', include('dj_rest_auth.registration.urls')),
    
    # Main API endpoints
    path('api/v1/', include(router.urls)),
]