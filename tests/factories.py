import factory
from factory.django import DjangoModelFactory
from django.contrib.auth.models import User
from accounts.models import Tenant, Domain, Branch, UserProfile
from main.models import Product, Category, Customer, Order, OrderItem
import uuid

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user_{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')

class TenantFactory(DjangoModelFactory):
    class Meta:
        model = Tenant

    name = factory.Sequence(lambda n: f'Tenant {n}')
    subdomain = factory.Sequence(lambda n: f'tenant{n}')
    schema_name = factory.LazyAttribute(lambda o: o.subdomain)

class DomainFactory(DjangoModelFactory):
    class Meta:
        model = Domain

    domain = factory.LazyAttribute(lambda o: f'{o.tenant.subdomain}.localhost')
    tenant = factory.SubFactory(TenantFactory)
    is_primary = True

class BranchFactory(DjangoModelFactory):
    class Meta:
        model = Branch

    tenant = factory.SubFactory(TenantFactory)
    name = factory.Sequence(lambda n: f'Branch {n}')
    currency_code = 'USD'
    currency_symbol = '$'

class UserProfileFactory(DjangoModelFactory):
    class Meta:
        model = UserProfile

    user = factory.SubFactory(UserFactory)
    tenant = factory.SubFactory(TenantFactory)
    branch = factory.SubFactory(BranchFactory, tenant=factory.SelfAttribute('..tenant'))
    role = 'admin'

class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    tenant = factory.SubFactory(TenantFactory)
    branch = factory.SubFactory(BranchFactory, tenant=factory.SelfAttribute('..tenant'))
    name = factory.Sequence(lambda n: f'Category {n}')

class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product

    tenant = factory.SubFactory(TenantFactory)
    branch = factory.SubFactory(BranchFactory, tenant=factory.SelfAttribute('..tenant'))
    category = factory.SubFactory(CategoryFactory, tenant=factory.SelfAttribute('..tenant'), branch=factory.SelfAttribute('..branch'))
    name = factory.Sequence(lambda n: f'Product {n}')
    sku = factory.Sequence(lambda n: f'SKU-{n}')
    price = 100.00
    cost_price = 50.00
    stock_quantity = 50

class CustomerFactory(DjangoModelFactory):
    class Meta:
        model = Customer

    tenant = factory.SubFactory(TenantFactory)
    branch = factory.SubFactory(BranchFactory, tenant=factory.SelfAttribute('..tenant'))
    name = factory.Sequence(lambda n: f'Customer {n}')
    phone = factory.Sequence(lambda n: f'+2348000000{n:03d}')
