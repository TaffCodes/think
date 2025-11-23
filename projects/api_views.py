from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import Project, ProjectAllocation, Service
from .serializers import ProjectSerializer, ServiceSerializer

class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by('-date_from')
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status']
    search_fields = ['company_name', 'contact_person']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def allocate_team(self, request, pk=None):
        """
        Assign a user to the project.
        Payload: { "user_id": 1 }
        """
        project = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if already allocated
        if ProjectAllocation.objects.filter(project=project, user_id=user_id).exists():
             return Response({'error': 'User already allocated'}, status=status.HTTP_400_BAD_REQUEST)

        ProjectAllocation.objects.create(
            project=project,
            user_id=user_id,
            allocated_by=request.user
        )
        return Response({'status': 'User allocated successfully'})