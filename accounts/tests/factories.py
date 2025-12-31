"""
Factory fixtures for accounts app tests.
"""
import factory
from factory.django import DjangoModelFactory
from faker import Faker
from accounts.models import Tenant, Domain, Branch, UserProfile
from django.contrib.auth.models import User

fake = Faker()


class TenantFactory(DjangoModelFactory):
    """Factory for creating test tenants."""
    
    class Meta:
        model = Tenant
    
    name = factory.Sequence(lambda n: f'Test Company {n}')
    subdomain = factory.Sequence(lambda n: f'test{n}')
    schema_name = factory.LazyAttribute(lambda obj: obj.subdomain)
    tenant_type = 'standard'


class DomainFactory(DjangoModelFactory):
    """Factory for creating tenant domains."""
    
    class Meta:
        model = Domain
    
    domain = factory.LazyAttribute(lambda obj: f'{obj.tenant.subdomain}.localhost')
    tenant = factory.SubFactory(TenantFactory)
    is_primary = True


class BranchFactory(DjangoModelFactory):
    """Factory for creating branches."""
    
    class Meta:
        model = Branch
    
    tenant = factory.SubFactory(TenantFactory)
    name = factory.Sequence(lambda n: f'Branch {n}')
    address = factory.Faker('address')
    phone = factory.Faker('phone_number')
    currency_symbol = '$'
    currency_code = 'USD'
    branch_type = 'retail'


class UserFactory(DjangoModelFactory):
    """Factory for creating Django users."""
    
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    
    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        if not create:
            return
        obj.set_password(extracted or 'testpass123')


class UserProfileFactory(DjangoModelFactory):
    """Factory for creating user profiles."""
    
    class Meta:
        model = UserProfile
    
    user = factory.SubFactory(UserFactory)
    tenant = factory.SubFactory(TenantFactory)
    branch = factory.SubFactory(BranchFactory)
    role = 'sales'
    can_perform_credit_sales = False
