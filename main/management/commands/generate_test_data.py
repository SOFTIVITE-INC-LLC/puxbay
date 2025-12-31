from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random

from accounts.models import Tenant, Branch
from main.models import Product, Customer, Order, OrderItem, Category


class Command(BaseCommand):
    help = 'Generate test data for POS system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--orders',
            type=int,
            default=50,
            help='Number of orders to create (default: 50)'
        )

    def handle(self, *args, **options):
        num_orders = options['orders']
        
        # Get the first tenant and branch
        try:
            tenant = Tenant.objects.first()
            if not tenant:
                self.stdout.write(self.style.ERROR('No tenant found. Please create a tenant first.'))
                return
            
            branches = Branch.objects.filter(tenant=tenant)
            if not branches.exists():
                self.stdout.write(self.style.ERROR('No branches found. Please create a branch first.'))
                return
            
            self.stdout.write(self.style.SUCCESS(f'Using tenant: {tenant.name}'))
            self.stdout.write(self.style.SUCCESS(f'Found {branches.count()} branch(es)'))
            
            # Create categories
            categories_data = ['Electronics', 'Clothing', 'Food & Beverage', 'Books', 'Home & Garden']
            categories = []
            for cat_name in categories_data:
                category, created = Category.objects.get_or_create(
                    name=cat_name,
                    tenant=tenant,
                    branch=branches.first()
                )
                categories.append(category)
                if created:
                    self.stdout.write(f'Created category: {cat_name}')
            
            # Create products
            products_data = [
                ('Laptop', 'LAP001', 899.99, 650.00),
                ('Wireless Mouse', 'MOU001', 29.99, 15.00),
                ('USB Cable', 'CAB001', 9.99, 3.00),
                ('T-Shirt', 'TSH001', 19.99, 8.00),
                ('Jeans', 'JEA001', 49.99, 25.00),
                ('Coffee Beans 1kg', 'COF001', 24.99, 12.00),
                ('Green Tea Box', 'TEA001', 14.99, 7.00),
                ('Novel Book', 'BOK001', 15.99, 8.00),
                ('Garden Tools Set', 'GAR001', 79.99, 40.00),
                ('Plant Pot', 'POT001', 12.99, 5.00),
            ]
            
            products = []
            for i, (name, sku, price, cost) in enumerate(products_data):
                for branch in branches:
                    product, created = Product.objects.get_or_create(
                        sku=f'{sku}-{branch.id}',
                        branch=branch,
                        defaults={
                            'name': name,
                            'tenant': tenant,
                            'price': Decimal(str(price)),
                            'cost_price': Decimal(str(cost)),
                            'stock_quantity': random.randint(50, 200),
                            'category': categories[i % len(categories)],
                            'is_active': True,
                        }
                    )
                    products.append(product)
                    if created:
                        self.stdout.write(f'Created product: {name} in {branch.name}')
            
            # Create customers
            customers_data = [
                ('John Doe', 'john@example.com', '555-0101'),
                ('Jane Smith', 'jane@example.com', '555-0102'),
                ('Bob Johnson', 'bob@example.com', '555-0103'),
                ('Alice Williams', 'alice@example.com', '555-0104'),
                ('Charlie Brown', 'charlie@example.com', '555-0105'),
            ]
            
            customers = []
            for name, email, phone in customers_data:
                customer, created = Customer.objects.get_or_create(
                    email=email,
                    tenant=tenant,
                    defaults={
                        'name': name,
                        'phone': phone,
                    }
                )
                customers.append(customer)
                if created:
                    self.stdout.write(f'Created customer: {name}')
            
            # Create orders
            self.stdout.write(self.style.SUCCESS(f'\nCreating {num_orders} orders...'))
            
            now = timezone.now()
            for i in range(num_orders):
                # Random date within last 60 days
                days_ago = random.randint(0, 60)
                order_date = now - timedelta(days=days_ago)
                
                # Random branch and customer
                branch = random.choice(list(branches))
                customer = random.choice(customers) if random.random() > 0.3 else None
                
                # Create order
                order = Order.objects.create(
                    tenant=tenant,
                    branch=branch,
                    customer=customer,
                    status='completed',
                    payment_method=random.choice(['cash', 'card', 'mobile']),
                    created_at=order_date,
                    updated_at=order_date,
                )
                
                # Add 1-5 random items to order
                num_items = random.randint(1, 5)
                branch_products = [p for p in products if p.branch == branch]
                selected_products = random.sample(branch_products, min(num_items, len(branch_products)))
                
                total_amount = Decimal('0.00')
                for product in selected_products:
                    quantity = random.randint(1, 3)
                    price = product.price
                    
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=price,
                    )
                    
                    total_amount += price * quantity
                
                # Update order total
                order.total_amount = total_amount
                order.amount_paid = total_amount
                order.save()
                
                if (i + 1) % 10 == 0:
                    self.stdout.write(f'Created {i + 1} orders...')
            
            self.stdout.write(self.style.SUCCESS(f'\n✓ Successfully created {num_orders} orders'))
            self.stdout.write(self.style.SUCCESS(f'✓ Created {len(products)} products across {branches.count()} branch(es)'))
            self.stdout.write(self.style.SUCCESS(f'✓ Created {len(customers)} customers'))
            self.stdout.write(self.style.SUCCESS('\nYou can now view the financial reports with data!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            import traceback
            traceback.print_exc()
