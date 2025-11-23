from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile

class UserSerializer(serializers.ModelSerializer):
    department = serializers.CharField(source='profile.department.name', read_only=True)
    is_verified = serializers.BooleanField(source='profile.is_verified', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'department', 'is_verified']