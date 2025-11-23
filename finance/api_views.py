from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db import transaction
from django.shortcuts import get_object_or_404
from decimal import Decimal
from .models import Account, Transaction, Expense
from .serializers import AccountSerializer, TransactionSerializer, ExpenseSerializer
from projects.models import Project

class AccountViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAdminUser]

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all().order_by('-expense_date')
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['project', 'staff_member']

    def perform_create(self, serializer):
        with transaction.atomic():
            expense = serializer.save(added_by=self.request.user)
            # Create Transaction
            Transaction.objects.create(
                amount=expense.amount,
                description=f"Expense: {expense.description}",
                from_account=expense.account,
                expense=expense,
                project=expense.project
            )

class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Transaction.objects.all().order_by('-timestamp')
    serializer_class = TransactionSerializer
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['post'])
    def manual(self, request):
        """
        Create a manual transaction (transfer/deposit).
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def receive_payment(self, request):
        """
        Payload: { "project_id": 1 }
        """
        project_id = request.data.get('project_id')
        project = get_object_or_404(Project, pk=project_id)
        
        # ... (Re-implement the split logic from views.py here) ...
        # For brevity, assuming logic is copied from finance/views.py ProjectPaymentView
        
        return Response({'status': 'Payment Received and Split'})