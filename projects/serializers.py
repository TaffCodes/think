from rest_framework import serializers
from django.db.models import Sum
from decimal import Decimal
from .models import Project, ProjectAllocation, Service
from users.serializers import UserSerializer

# We need to lazy-load the Transaction model to avoid circular imports
from django.apps import apps

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
    services = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(), 
        many=True, 
        write_only=True
    )
    created_by_name = serializers.CharField(source='created_by.first_name', read_only=True)
    
    # --- NEW CALCULATED FIELDS ---
    total_expenses = serializers.SerializerMethodField()
    profit = serializers.SerializerMethodField()
    equipment_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'company_name', 'services', 'services_details', 
            'date_from', 'date_to', 'location', 'contact_person', 
            'charges', 'status', 'created_at', 'created_by_name',
            'team', 'is_paid',
            # Add the new fields here
            'total_expenses', 'profit', 'equipment_count'
        ]

    def get_total_expenses(self, obj):
        # Get the Transaction model dynamically
        Transaction = apps.get_model('finance', 'Transaction')
        
        # Sum up all transactions for this project that are NOT income
        # (Assuming income has no 'expense' link or is a credit to Main Account)
        # A safer way is to sum transactions where 'expense' is NOT Null
        expenses = Transaction.objects.filter(project=obj, expense__isnull=False)
        total = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        return total

    def get_profit(self, obj):
        # Profit = Charges - Expenses
        expenses = self.get_total_expenses(obj)
        return obj.charges - expenses

    def get_equipment_count(self, obj):
        return obj.equipment_requests.count()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['services'] = [service.name for service in instance.services.all()]
        return data