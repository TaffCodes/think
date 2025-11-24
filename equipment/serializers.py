# equipment/serializers.py
# (Complete, Updated File)

from rest_framework import serializers
from .models import EquipmentItem, EquipmentCategory, EquipmentRequest, RequestedItem, CheckoutLog
from users.serializers import UserSerializer
from projects.serializers import ProjectSerializer
from projects.models import Project

# --- Helper Serializers for Nesting ---

class EquipmentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentCategory
        fields = ['id', 'name']

class SimpleProjectSerializer(serializers.ModelSerializer):
    """
    Expanded to include fields the frontend expects for formatting (charges, dates).
    """
    class Meta:
        from projects.models import Project
        model = Project
        # Added charges, status, and dates to prevent frontend crashes
        fields = ['id', 'company_name', 'charges', 'status', 'date_from', 'date_to']

class SimpleUserSerializer(serializers.ModelSerializer):
    """Minimal user info"""
    class Meta:
        from django.contrib.auth.models import User
        model = User
        fields = ['id', 'username', 'email']

# --- Main Serializers ---

class EquipmentItemSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=EquipmentCategory.objects.all())
    available_quantity = serializers.IntegerField(read_only=True)
    damaged_quantity = serializers.IntegerField(source='get_damaged_quantity', read_only=True)
    committed_quantity = serializers.IntegerField(source='get_committed_quantity', read_only=True)

    class Meta:
        model = EquipmentItem
        fields = ['id', 'name', 'category', 'total_quantity', 'available_quantity', 'damaged_quantity', 'committed_quantity']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['category'] = EquipmentCategorySerializer(instance.category).data
        return response

class RequestedItemSerializer(serializers.ModelSerializer):
    item = serializers.PrimaryKeyRelatedField(queryset=EquipmentItem.objects.all())

    class Meta:
        model = RequestedItem
        fields = ['id', 'item', 'quantity']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['item'] = EquipmentItemSerializer(instance.item).data
        return response

class CheckoutLogSerializer(serializers.ModelSerializer):
    item = serializers.PrimaryKeyRelatedField(queryset=EquipmentItem.objects.all())
    checked_out_by = serializers.PrimaryKeyRelatedField(read_only=True)
    
    # FIX 2: Manually add 'quantity' back to the API response (always 1)
    # This prevents frontend crashes if it tries to read log.quantity
    quantity = serializers.SerializerMethodField()

    class Meta:
        model = CheckoutLog
        fields = '__all__'

    def get_quantity(self, obj):
        return 1

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['item'] = EquipmentItemSerializer(instance.item).data
        response['checked_out_by'] = SimpleUserSerializer(instance.checked_out_by).data
        if instance.checked_in_by:
            response['checked_in_by'] = SimpleUserSerializer(instance.checked_in_by).data
        return response

class EquipmentRequestSerializer(serializers.ModelSerializer):
    items = RequestedItemSerializer(many=True, read_only=True)
    logs = CheckoutLogSerializer(many=True, read_only=True)
    
    project = serializers.PrimaryKeyRelatedField(
                queryset=Project.objects.all()
    )
    requested_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = EquipmentRequest
        fields = [
            'id', 'project', 'requested_by', 'status', 
            'created_at', 'admin_notes', 'items', 'logs'
        ]

    def to_representation(self, instance):
        response = super().to_representation(instance)
        
        # Convert Project ID to Full Object (now with charges/dates)
        if instance.project:
            response['project'] = SimpleProjectSerializer(instance.project).data
        
        if instance.requested_by:
            response['requested_by'] = SimpleUserSerializer(instance.requested_by).data
            
        return response