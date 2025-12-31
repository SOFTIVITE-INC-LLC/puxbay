from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Tenant, Branch, UserProfile
from main.models import Category, Product, Customer
from datetime import date, timedelta
import random
import requests
from django.core.files.base import ContentFile

class Command(BaseCommand):
    help = 'Populates the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Populating data...')

        # 1. Create Tenant
        tenant, created = Tenant.objects.get_or_create(
            subdomain='techstore',
            defaults={'name': 'TechStore Inc.', 'address': '123 Tech Valley, Silicon City'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created Tenant: {tenant.name}'))
        else:
            self.stdout.write(f'Tenant {tenant.name} already exists')

        # 2. Create Branch
        branch, created = Branch.objects.get_or_create(
            name='Downtown HQ',
            tenant=tenant,
            defaults={'address': '456 Main St, Downtown', 'phone': '555-0123'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created Branch: {branch.name}'))

        # 3. Create Users
        users_data = [
            {'username': 'admin_user', 'email': 'admin@techstore.com', 'role': 'admin', 'password': 'password123'},
            {'username': 'manager_user', 'email': 'manager@techstore.com', 'role': 'manager', 'password': 'password123'},
            {'username': 'sales_user', 'email': 'sales@techstore.com', 'role': 'sales', 'password': 'password123'},
            {'username': 'finance_user', 'email': 'finance@techstore.com', 'role': 'financial', 'password': 'password123'},
        ]

        for u_data in users_data:
            if not User.objects.filter(username=u_data['username']).exists():
                user = User.objects.create_user(
                    username=u_data['username'],
                    email=u_data['email'],
                    password=u_data['password']
                )
                UserProfile.objects.create(
                    user=user,
                    tenant=tenant,
                    branch=branch,
                    role=u_data['role']
                )
                self.stdout.write(self.style.SUCCESS(f'Created User: {u_data["username"]} ({u_data["role"]})'))
            else:
                 self.stdout.write(f'User {u_data["username"]} already exists')

        # 4. Create Categories
        categories_data = [
            {'name': 'Laptops', 'desc': 'High performance computers'},
            {'name': 'Smartphones', 'desc': 'Mobile devices and accessories'},
            {'name': 'Audio', 'desc': 'Headphones and speakers'},
            {'name': 'Accessories', 'desc': 'Cables, cases, and chargers'},
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                tenant=tenant,
                branch=branch,
                defaults={'description': cat_data['desc']}
            )
            categories.append(category)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created Category: {category.name}'))

        # 5. Create Products
        products_data = [
            {'name': 'MacBook Pro 14"', 'price': 1999.00, 'cost': 1700.00, 'sku': 'MBP14', 'cat': 'Laptops', 'img': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800'},
            {'name': 'Dell XPS 15', 'price': 1500.00, 'cost': 1200.00, 'sku': 'DXPS15', 'cat': 'Laptops', 'img': 'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=800'},
            {'name': 'iPhone 15 Pro', 'price': 999.00, 'cost': 850.00, 'sku': 'IP15P', 'cat': 'Smartphones', 'img': 'https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=800'},
            {'name': 'Samsung S24 Ultra', 'price': 1199.00, 'cost': 950.00, 'sku': 'S24U', 'cat': 'Smartphones', 'img': 'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=800'},
            {'name': 'Sony WH-1000XM5', 'price': 349.00, 'cost': 280.00, 'sku': 'SONYXM5', 'cat': 'Audio', 'img': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800'},
            {'name': 'AirPods Pro 2', 'price': 249.00, 'cost': 190.00, 'sku': 'APP2', 'cat': 'Audio', 'img': 'https://images.unsplash.com/photo-1588423770670-45731ff1f39b?w=800'},
            {'name': 'USB-C Cable', 'price': 19.99, 'cost': 5.00, 'sku': 'USBC2M', 'cat': 'Accessories', 'img': 'https://images.unsplash.com/photo-1589492477829-5e65395b66cc?w=800'},
            {'name': 'Laptop Stand', 'price': 49.99, 'cost': 20.00, 'sku': 'LPSTND', 'cat': 'Accessories', 'img': 'https://images.unsplash.com/photo-1527443154391-507e9dc6c5cc?w=800'},
        ]

        for p_data in products_data:
            # Find category object
            cat = next((c for c in categories if c.name == p_data['cat']), None)
            
            product, created = Product.objects.get_or_create(
                sku=p_data['sku'],
                tenant=tenant,
                branch=branch,
                defaults={
                    'name': p_data['name'],
                    'category': cat,
                    'price': p_data['price'],
                    'cost_price': p_data['cost'],
                    'stock_quantity': random.randint(5, 50),
                    'low_stock_threshold': 5,
                    'barcode': str(random.randint(10000000, 99999999)),
                    'description': f"Premium {p_data['name']}",
                    'is_active': True
                }
            )
            if created:
                # Add image if available
                if p_data.get('img'):
                    try:
                        resp = requests.get(p_data['img'], timeout=5)
                        if resp.status_code == 200:
                            product.image.save(f"{product.sku}.jpg", ContentFile(resp.content), save=True)
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"Could not download image for {product.name}: {e}"))
                self.stdout.write(self.style.SUCCESS(f'Created Product: {product.name}'))

        # 6. Create Customers
        customers_data = [
            {'name': 'John Doe', 'email': 'john@example.com', 'phone': '555-1111'},
            {'name': 'Jane Smith', 'email': 'jane@example.com', 'phone': '555-2222'},
            {'name': 'Bob Johnson', 'email': 'bob@example.com', 'phone': '555-3333'},
        ]

        for c_data in customers_data:
            cust, created = Customer.objects.get_or_create(
                email=c_data['email'],
                tenant=tenant,
                defaults={
                    'name': c_data['name'],
                    'phone': c_data['phone'],
                    'address': '123 Customer Lane'
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created Customer: {cust.name}'))

        self.stdout.write(self.style.SUCCESS('Data population complete!'))
