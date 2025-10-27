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
]

# --- ADD THIS AT THE BOTTOM ---
# This is required to serve user-uploaded files (like receipts) during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)