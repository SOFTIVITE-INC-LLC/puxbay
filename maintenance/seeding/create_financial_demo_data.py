"""
Script to create demo financial data for testing
Run with: python manage.py shell < create_financial_demo_data.py
"""

from django.contrib.auth.models import User
from accounts.models import Tenant, UserProfile, Branch
from main.models import (
    ExpenseCategory, Expense, TaxConfiguration, PaymentMethod,
    Product, Customer, Order, OrderItem, Return, ReturnItem
)
from decimal import Decimal
from datetime import datetime, timedelta
import random

# Get or create test tenant
try:
    user = User.objects.first()
    if not user:
        print("No users found. Please create a user first.")
        exit()
    
    profile = user.profile
    tenant = profile.tenant
    branch = tenant.branches.first()
    
    if not branch:
        print("No branches found. Please create a branch first.")
        exit()
    
    print(f"Using tenant: {tenant.name}")
    print(f"Using branch: {branch.name}")
    
    # Create Tax Configuration
    tax_config, created = TaxConfiguration.objects.get_or_create(
        tenant=tenant,
        defaults={
            'tax_type': 'sales_tax',
            'tax_rate': Decimal('15.00'),
            'tax_number': 'TAX-123456',
            'include_tax_in_prices': False,
            'is_active': True
        }
    )
    print(f"Tax Configuration: {'Created' if created else 'Already exists'}")
    
    # Create Expense Categories
    categories_data = [
        ('Rent', 'fixed'),
        ('Utilities', 'fixed'),
        ('Salaries', 'fixed'),
        ('Marketing', 'variable'),
        ('Supplies', 'variable'),
        ('Maintenance', 'variable'),
    ]
    
    categories = []
    for name, cat_type in categories_data:
        category, created = ExpenseCategory.objects.get_or_create(
            tenant=tenant,
            name=name,
            defaults={'type': cat_type}
        )
        categories.append(category)
        if created:
            print(f"Created expense category: {name}")
    
    # Create Expenses
    today = datetime.now().date()
    for i in range(20):
        days_ago = random.randint(0, 60)
        expense_date = today - timedelta(days=days_ago)
        category = random.choice(categories)
        
        amount = Decimal(random.randint(100, 5000))
        
        Expense.objects.create(
            tenant=tenant,
            branch=branch if random.random() > 0.3 else None,
            category=category,
            amount=amount,
            date=expense_date,
            description=f"Sample {category.name.lower()} expense",
            created_by=profile
        )
    
    print(f"Created 20 sample expenses")
    
    # Create Payment Methods
    payment_methods_data = [
        ('Stripe Payments', 'stripe', 'sk_test_1234'),
        ('PayPal', 'paypal', 'pp_1234'),
        ('Cash Register', 'cash', ''),
        ('Card Terminal', 'card', ''),
    ]
    
    for name, provider, hint in payment_methods_data:
        method, created = PaymentMethod.objects.get_or_create(
            tenant=tenant,
            name=name,
            defaults={
                'provider': provider,
                'api_key_hint': hint,
                'is_active': True
            }
        )
        if created:
            print(f"Created payment method: {name}")
    
    print("\n✅ Demo financial data created successfully!")
    print("\nYou can now:")
    print("1. View expenses at /financial/expenses/")
    print("2. Generate P&L report at /financial/reports/profit-loss/")
    print("3. View tax reports at /financial/reports/tax/")
    print("4. Configure payment gateways at /financial/payments/settings/")
    print("5. Manage returns at /financial/returns/")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
