from rest_framework import serializers
from .models import Account, Transaction, Expense

class AccountSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(source='get_balance', max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = Account
        fields = ['id', 'name', 'balance']

class TransactionSerializer(serializers.ModelSerializer):
    from_account_name = serializers.CharField(source='from_account.name', read_only=True)
    to_account_name = serializers.CharField(source='to_account.name', read_only=True)
    project_name = serializers.CharField(source='project.company_name', read_only=True)

    class Meta:
        model = Transaction
        fields = '__all__'

class ExpenseSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.company_name', read_only=True)
    staff_name = serializers.CharField(source='staff_member.username', read_only=True)
    account_name = serializers.CharField(source='account.name', read_only=True)
    receipt_url = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = '__all__'

    def get_receipt_url(self, obj):
        if obj.receipt:
            return obj.receipt.url
        return None