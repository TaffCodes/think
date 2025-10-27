# projects/urls.py
# (Create this file)

from django.urls import path
from .views import (
    ProjectListView, 
    ProjectDetailView, 
    ProjectCreateView
)

urlpatterns = [
    path('', ProjectListView.as_view(), name='project-list'),
    path('new/', ProjectCreateView.as_view(), name='project-create'),
    path('<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    # We will add URLs for update, delete, and allocation later.
]