"""
Tests for payment processing functionality.

Critical tests for payment service including credit authorization,
limit enforcement, split payments, and transaction atomicity.
"""
import pytest
from decimal import Decimal
from django_tenants.utils import schema_context
from branches.services.payments import PaymentService
from main.tests.factories import ProductFactory, CustomerFactory
from accounts.tests.factories import UserProfileFactory


@pytest.mark.django_db
class TestCreditPayments:
    """Test credit payment processing and authorization."""
    
    def test_unauthorized_sales_staff_cannot_process_credit(self, test_tenant, test_branch, sales_user):
        """Sales staff without permission should not be able to process credit transactions."""
        with schema_context(test_tenant.schema_name):
            # Create customer with credit limit
            customer = CustomerFactory(
                tenant=test_tenant,
                credit_limit=Decimal('1000.00'),
                outstanding_debt=Decimal('0.00')
            )
            
            # Create product
            product = ProductFactory(
                tenant=test_tenant,
                branch=test_branch,
                price=Decimal('100.00')
            )
            
            # Get user profile
            user_profile = sales_user.profiles.get(tenant=test_tenant)
            
            # Attempt credit payment
            service = PaymentService(user_profile=user_profile, branch=test_branch, tenant=test_tenant)
            
            result = service.process_checkout(
                items=[{'product_id': str(product.id), 'quantity': 1}],
                payments=[{'method': 'credit', 'amount': 100.00}],
                customer_id=str(customer.id)
            )
            
            assert result['success'] is False
            assert 'permission' in result['error'].lower()
    
    def test_authorized_sales_staff_can_process_credit(self, test_tenant, test_branch, sales_user_with_credit):
        """Sales staff with permission should be able to process credit transactions."""
        with schema_context(test_tenant.schema_name):
            customer = CustomerFactory(
                tenant=test_tenant,
                credit_limit=Decimal('1000.00'),
                outstanding_debt=Decimal('0.00')
            )
            
            product = ProductFactory(
                tenant=test_tenant,
                branch=test_branch,
                price=Decimal('100.00'),
                stock_quantity=10
            )
            
            user_profile = sales_user_with_credit.profiles.get(tenant=test_tenant)
            
            service = PaymentService(user_profile=user_profile, branch=test_branch, tenant=test_tenant)
            
            result = service.process_checkout(
                items=[{'product_id': str(product.id), 'quantity': 1}],
                payments=[{'method': 'credit', 'amount': 100.00}],
                customer_id=str(customer.id)
            )
            
            assert result['success'] is True
            
            # Verify customer debt increased
            customer.refresh_from_db()
            assert customer.outstanding_debt == Decimal('100.00')
    
    def test_credit_limit_enforcement(self, test_tenant, test_branch, admin_user):
        """Credit transactions should not exceed customer's credit limit."""
        with schema_context(test_tenant.schema_name):
            customer = CustomerFactory(
                tenant=test_tenant,
                credit_limit=Decimal('500.00'),
                outstanding_debt=Decimal('400.00')
            )
            
            product = ProductFactory(
                tenant=test_tenant,
                branch=test_branch,
                price=Decimal('200.00')
            )
            
            user_profile = admin_user.profiles.get(tenant=test_tenant)
            service = PaymentService(user_profile=user_profile, branch=test_branch, tenant=test_tenant)
            
            result = service.process_checkout(
                items=[{'product_id': str(product.id), 'quantity': 1}],
                payments=[{'method': 'credit', 'amount': 200.00}],
                customer_id=str(customer.id)
            )
            
            assert result['success'] is False
            assert 'credit limit exceeded' in result['error'].lower()
    
    def test_admin_bypass_credit_permission(self, test_tenant, test_branch, admin_user):
        """Admin users should bypass credit permission checks."""
        with schema_context(test_tenant.schema_name):
            customer = CustomerFactory(
                tenant=test_tenant,
                credit_limit=Decimal('1000.00')
            )
            
            product = ProductFactory(
                tenant=test_tenant,
                branch=test_branch,
                price=Decimal('100.00'),
                stock_quantity=10
            )
            
            user_profile = admin_user.profiles.get(tenant=test_tenant)
            service = PaymentService(user_profile=user_profile, branch=test_branch, tenant=test_tenant)
            
            result = service.process_checkout(
                items=[{'product_id': str(product.id), 'quantity': 1}],
                payments=[{'method': 'credit', 'amount': 100.00}],
                customer_id=str(customer.id)
            )
            
            assert result['success'] is True


@pytest.mark.django_db
class TestSplitPayments:
    """Test split payment functionality."""
    
    def test_split_payment_validation(self, test_tenant, test_branch, admin_user):
        """Split payments should sum to total amount."""
        with schema_context(test_tenant.schema_name):
            product = ProductFactory(
                tenant=test_tenant,
                branch=test_branch,
                price=Decimal('100.00'),
                stock_quantity=10
            )
            
            user_profile = admin_user.profiles.get(tenant=test_tenant)
            service = PaymentService(user_profile=user_profile, branch=test_branch, tenant=test_tenant)
            
            # Insufficient payment
            result = service.process_checkout(
                items=[{'product_id': str(product.id), 'quantity': 1}],
                payments=[
                    {'method': 'cash', 'amount': 50.00},
                    {'method': 'card', 'amount': 30.00}
                ]
            )
            
            assert result['success'] is False
            assert 'insufficient payment' in result['error'].lower()
    
    def test_successful_split_payment(self, test_tenant, test_branch, admin_user):
        """Valid split payments should process successfully."""
        with schema_context(test_tenant.schema_name):
            product = ProductFactory(
                tenant=test_tenant,
                branch=test_branch,
                price=Decimal('100.00'),
                stock_quantity=10
            )
            
            user_profile = admin_user.profiles.get(tenant=test_tenant)
            service = PaymentService(user_profile=user_profile, branch=test_branch, tenant=test_tenant)
            
            result = service.process_checkout(
                items=[{'product_id': str(product.id), 'quantity': 1}],
                payments=[
                    {'method': 'cash', 'amount': 60.00},
                    {'method': 'card', 'amount': 40.00}
                ]
            )
            
            assert result['success'] is True
            assert result['order']['payment_method'] == 'split'
