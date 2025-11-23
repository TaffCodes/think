from rest_framework import serializers
from .models import EquipmentItem, EquipmentCategory, EquipmentRequest, RequestedItem, CheckoutLog
from projects.serializers import ProjectSerializer
from users.serializers import UserSerializer

class EquipmentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentCategory
        fields = ['id', 'name']

class EquipmentItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    available_quantity = serializers.IntegerField(read_only=True)
    damaged_quantity = serializers.IntegerField(source='get_damaged_quantity', read_only=True)
    committed_quantity = serializers.IntegerField(source='get_committed_quantity', read_only=True)

    class Meta:
        model = EquipmentItem
        fields = ['id', 'name', 'category', 'category_name', 'total_quantity', 'available_quantity', 'damaged_quantity', 'committed_quantity']

class RequestedItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    item_category = serializers.CharField(source='item.category.name', read_only=True)

    class Meta:
        model = RequestedItem
        fields = ['id', 'item', 'item_name', 'item_category', 'quantity']

class CheckoutLogSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    checked_out_by_name = serializers.CharField(source='checked_out_by.username', read_only=True)
    
    class Meta:
        model = CheckoutLog
        fields = '__all__'

class EquipmentRequestSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.company_name', read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.username', read_only=True)
    items = RequestedItemSerializer(many=True, read_only=True)
    logs = CheckoutLogSerializer(many=True, read_only=True)

    class Meta:
        model = EquipmentRequest
        fields = ['id', 'project', 'project_name', 'requested_by', 'requested_by_name', 'status', 'created_at', 'admin_notes', 'items', 'logs']