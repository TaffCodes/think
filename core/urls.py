# core/urls.py
#
# This file contains the URL routing for our 'core' app

from django.urls import path
from .views import DashboardView

urlpatterns = [
    # We name this 'dashboard' to match LOGIN_REDIRECT_URL in settings.py
    path('', DashboardView.as_view(), name='dashboard'),
]