import pytest
from django.conf import settings
from django_tenants.utils import schema_context, tenant_context
from tests.factories import (
    TenantFactory, DomainFactory, BranchFactory, 
    UserFactory, UserProfileFactory, ProductFactory, CategoryFactory
)

@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """
    Setup test database with public schema.
    """
    with django_db_blocker.unblock():
        # Public schema is created automatically by django-tenants
        pass

@pytest.fixture
def test_tenant(db):
    """
    Create a test tenant with schema using factory.
    """
    tenant = TenantFactory()
    DomainFactory(tenant=tenant)
    return tenant

@pytest.fixture
def test_branch(test_tenant):
    """
    Create a test branch for the test tenant.
    """
    with schema_context(test_tenant.schema_name):
        return BranchFactory(tenant=test_tenant)

@pytest.fixture
def admin_user(test_tenant):
    """
    Create an admin user for the test tenant.
    """
    user = UserFactory(username='admin')
    with schema_context(test_tenant.schema_name):
        UserProfileFactory(user=user, tenant=test_tenant, role='admin')
    return user

@pytest.fixture
def manager_user(test_tenant, test_branch):
    """
    Create a manager user for the test tenant.
    """
    user = UserFactory(username='manager')
    with schema_context(test_tenant.schema_name):
        UserProfileFactory(user=user, tenant=test_tenant, branch=test_branch, role='manager')
    return user

@pytest.fixture
def sales_user(test_tenant, test_branch):
    """
    Create a sales user for the test tenant.
    """
    user = UserFactory(username='sales')
    with schema_context(test_tenant.schema_name):
        UserProfileFactory(
            user=user, 
            tenant=test_tenant, 
            branch=test_branch, 
            role='sales',
            can_perform_credit_sales=False
        )
    return user

@pytest.fixture
def test_product(test_tenant, test_branch):
    """
    Create a test product for the test tenant/branch.
    """
    with schema_context(test_tenant.schema_name):
        return ProductFactory(tenant=test_tenant, branch=test_branch)

@pytest.fixture
def authenticated_client(client, admin_user):
    """
    Create an authenticated Django test client.
    """
    client.force_login(admin_user)
    return client
