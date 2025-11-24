from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db import transaction
from decimal import Decimal
from .models import Account, Transaction, Expense
from .serializers import AccountSerializer, TransactionSerializer, ExpenseSerializer
from projects.models import Project

# Accounts are generally read-only for the frontend, but if you want 
# to create them via API later, you can change this to ModelViewSet too.
class AccountViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAdminUser]

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all().order_by('-expense_date')
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        project = self.request.query_params.get('project')
        staff = self.request.query_params.get('staff')
        if project:
            queryset = queryset.filter(project_id=project)
        if staff:
            queryset = queryset.filter(staff_member_id=staff)
        return queryset

    def perform_create(self, serializer):
        with transaction.atomic():
            expense = serializer.save(added_by=self.request.user)
            # Automatically create the transaction ledger entry
            Transaction.objects.create(
                amount=expense.amount,
                description=f"Expense: {expense.description}",
                from_account=expense.account,
                expense=expense,
                project=expense.project
            )

# --- THIS IS THE FIXED CLASS ---
# Changed from ReadOnlyModelViewSet to ModelViewSet
class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all().order_by('-timestamp')
    serializer_class = TransactionSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        # Manual transaction creation
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='receive-payment')
    def receive_payment(self, request):
        project_id = request.data.get('project_id')
        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return Response({'error': 'Project not found'}, status=404)

        if project.is_paid:
            return Response({'error': 'Project already paid'}, status=400)

        try:
            with transaction.atomic():
                # 1. Get Main Accounts
                main_acc = Account.objects.get(name__iexact="Main Account")
                logistics_acc = Account.objects.get(name__iexact="Logistics")
                admin_acc = Account.objects.get(name__iexact="Admin")
                
                project.is_paid = True
                project.save()
                
                # 2. Income (Credit Main Account)
                Transaction.objects.create(
                    amount=project.charges, 
                    description=f"Payment: {project.company_name}",
                    to_account=main_acc, 
                    project=project
                )
                
                # 3. Standard Splits
                Transaction.objects.create(
                    amount=project.charges * Decimal('0.10'), 
                    description="Logistics Split",
                    from_account=main_acc, 
                    to_account=logistics_acc, 
                    project=project
                )
                
                Transaction.objects.create(
                    amount=project.charges * Decimal('0.15'), 
                    description="Admin Split",
                    from_account=main_acc, 
                    to_account=admin_acc, 
                    project=project
                )
                
                # 4. Department Split (The Logic Fix)
                dept_cut_total = project.charges * Decimal('0.35')
                
                # Find unique department NAMES from the project's services
                # Note: This relies on you setting the 'department' in the Service model
                involved_dept_names = project.services.values_list('department__name', flat=True).distinct()
                
                # Find Accounts that match these Department names
                dept_accounts = Account.objects.filter(name__in=involved_dept_names)
                
                if dept_accounts.exists():
                    # Split the 35% cut equally among involved departments
                    split_amt = dept_cut_total / dept_accounts.count()
                    
                    for acc in dept_accounts:
                        Transaction.objects.create(
                            amount=split_amt, 
                            description=f"Dept Split ({acc.name})",
                            from_account=main_acc, 
                            to_account=acc, 
                            project=project
                        )
                else:
                    # Fallback if services have no departments assigned yet
                    # Money stays in Main or you could log a warning
                    pass

            return Response({'status': 'Payment received and split'})
            
        except Account.DoesNotExist as e:
            return Response({'error': f'Required account missing: {str(e)}'}, status=500)
        except Exception as e:
            return Response({'error': str(e)}, status=500)