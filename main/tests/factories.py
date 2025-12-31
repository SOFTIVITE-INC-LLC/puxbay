"""
Factory fixtures for main app tests.
"""
import factory
from factory.django import DjangoModelFactory
from faker import Faker
from main.models import Product, Category, Customer, Supplier
from accounts.tests.factories import TenantFactory, BranchFactory
from decimal import Decimal

fake = Faker()


class CategoryFactory(DjangoModelFactory):
    """Factory for creating product categories."""
    
    class Meta:
        model = Category
    
    tenant = factory.SubFactory(TenantFactory)
    branch = factory.SubFactory(BranchFactory)
    name = factory.Sequence(lambda n: f'Category {n}')
    description = factory.Faker('text', max_nb_chars=200)


class ProductFactory(DjangoModelFactory):
    """Factory for creating products."""
    
    class Meta:
        model = Product
    
    tenant = factory.SubFactory(TenantFactory)
    branch = factory.SubFactory(BranchFactory)
    name = factory.Sequence(lambda n: f'Product {n}')
    sku = factory.Sequence(lambda n: f'SKU{n:05d}')
    category = factory.SubFactory(CategoryFactory)
    price = factory.LazyFunction(lambda: Decimal(fake.random_int(min=10, max=1000)))
    cost = factory.LazyAttribute(lambda obj: obj.price * Decimal('0.6'))
    stock_quantity = factory.LazyFunction(lambda: fake.random_int(min=0, max=100))
    reorder_level = 10
    is_active = True


class CustomerFactory(DjangoModelFactory):
    """Factory for creating customers."""
    
    class Meta:
        model = Customer
    
    tenant = factory.SubFactory(TenantFactory)
    name = factory.Faker('name')
    email = factory.Faker('email')
    phone = factory.Faker('phone_number')
    address = factory.Faker('address')
    credit_limit = factory.LazyFunction(lambda: Decimal(fake.random_int(min=0, max=10000)))
    outstanding_debt = Decimal('0.00')
    loyalty_points = 0
    store_credit_balance = Decimal('0.00')


class SupplierFactory(DjangoModelFactory):
    """Factory for creating suppliers."""
    
    class Meta:
        model = Supplier
    
    tenant = factory.SubFactory(TenantFactory)
    name = factory.Faker('company')
    contact_person = factory.Faker('name')
    email = factory.Faker('company_email')
    phone = factory.Faker('phone_number')
    address = factory.Faker('address')
    payment_terms = 'Net 30'
    credit_limit = factory.LazyFunction(lambda: Decimal(fake.random_int(min=0, max=50000)))
    outstanding_balance = Decimal('0.00')
    is_active = True
