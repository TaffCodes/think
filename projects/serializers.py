from rest_framework import serializers
from .models import Project, ProjectAllocation, Service
from users.serializers import UserSerializer

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name']

class ProjectAllocationSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = ProjectAllocation
        fields = ['id', 'user', 'user_details', 'allocated_at']

class ProjectSerializer(serializers.ModelSerializer):
    services_details = ServiceSerializer(source='services', many=True, read_only=True)
    team = ProjectAllocationSerializer(many=True, read_only=True)
    team_count = serializers.IntegerField(source='team.count', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'company_name', 'services', 'services_details', 
            'date_from', 'date_to', 'location', 'contact_person', 
            'charges', 'status', 'created_at', 'created_by_name',
            'team', 'team_count', 'is_paid', 'description' # Assuming description exists or remove if not
        ]