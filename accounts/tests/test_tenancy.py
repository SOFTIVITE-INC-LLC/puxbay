"""
Tests for multi-tenancy data isolation.

Critical tests to ensure data doesn't leak between tenants.
"""
import pytest
from django_tenants.utils import schema_context
from main.models import Product, Customer
from main.tests.factories import ProductFactory, CustomerFactory
from accounts.tests.factories import TenantFactory, BranchFactory


@pytest.mark.django_db
class TestTenantIsolation:
    """Test that data is properly isolated between tenants."""
    
    def test_products_isolated_between_tenants(self, db):
        """Products from one tenant should not be visible to another."""
        # Create two separate tenants
        tenant1 = TenantFactory(subdomain='tenant1', schema_name='tenant1')
        tenant2 = TenantFactory(subdomain='tenant2', schema_name='tenant2')
        
        branch1 = BranchFactory(tenant=tenant1)
        branch2 = BranchFactory(tenant=tenant2)
        
        # Create products in each tenant's schema
        with schema_context(tenant1.schema_name):
            product1 = ProductFactory(tenant=tenant1, branch=branch1, name='Tenant 1 Product')
        
        with schema_context(tenant2.schema_name):
            product2 = ProductFactory(tenant=tenant2, branch=branch2, name='Tenant 2 Product')
        
        # Verify isolation
        with schema_context(tenant1.schema_name):
            products = Product.objects.all()
            assert products.count() == 1
            assert products.first().name == 'Tenant 1 Product'
        
        with schema_context(tenant2.schema_name):
            products = Product.objects.all()
            assert products.count() == 1
            assert products.first().name == 'Tenant 2 Product'
    
    def test_customers_isolated_between_tenants(self, db):
        """Customers from one tenant should not be visible to another."""
        tenant1 = TenantFactory(subdomain='tenant1', schema_name='tenant1')
        tenant2 = TenantFactory(subdomain='tenant2', schema_name='tenant2')
        
        with schema_context(tenant1.schema_name):
            customer1 = CustomerFactory(tenant=tenant1, name='Customer A')
        
        with schema_context(tenant2.schema_name):
            customer2 = CustomerFactory(tenant=tenant2, name='Customer B')
        
        # Verify isolation
        with schema_context(tenant1.schema_name):
            customers = Customer.objects.all()
            assert customers.count() == 1
            assert customers.first().name == 'Customer A'
        
        with schema_context(tenant2.schema_name):
            customers = Customer.objects.all()
            assert customers.count() == 1
            assert customers.first().name == 'Customer B'
    
    def test_cross_tenant_query_prevention(self, db):
        """Attempting to access another tenant's data should fail."""
        tenant1 = TenantFactory(subdomain='tenant1', schema_name='tenant1')
        tenant2 = TenantFactory(subdomain='tenant2', schema_name='tenant2')
        
        branch1 = BranchFactory(tenant=tenant1)
        
        with schema_context(tenant1.schema_name):
            product1 = ProductFactory(tenant=tenant1, branch=branch1)
            product1_id = product1.id
        
        # Try to access tenant1's product from tenant2's schema
        with schema_context(tenant2.schema_name):
            with pytest.raises(Product.DoesNotExist):
                Product.objects.get(id=product1_id)


@pytest.mark.django_db
class TestSchemaContext:
    """Test schema context switching."""
    
    def test_schema_context_switches_correctly(self, test_tenant):
        """Schema context should properly switch between tenants."""
        tenant2 = TenantFactory(subdomain='tenant2', schema_name='tenant2')
        branch1 = BranchFactory(tenant=test_tenant)
        branch2 = BranchFactory(tenant=tenant2)
        
        # Create product in first tenant
        with schema_context(test_tenant.schema_name):
            ProductFactory(tenant=test_tenant, branch=branch1, name='Product 1')
            count1 = Product.objects.count()
        
        # Create product in second tenant
        with schema_context(tenant2.schema_name):
            ProductFactory(tenant=tenant2, branch=branch2, name='Product 2')
            count2 = Product.objects.count()
        
        # Both should have exactly 1 product
        assert count1 == 1
        assert count2 == 1
        
        # Verify names are different
        with schema_context(test_tenant.schema_name):
            assert Product.objects.first().name == 'Product 1'
        
        with schema_context(tenant2.schema_name):
            assert Product.objects.first().name == 'Product 2'
