"""
Comprehensive API tests for the POS System API.
Tests cover authentication, products, orders, and customers endpoints.
"""

from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from accounts.models import Tenant, Branch, UserProfile
from main.models import Product, Category, Order, OrderItem, Customer


class APITestMixin:
    """Mixin to set up tenant, branch, and authenticated user for API tests."""
    
    @classmethod
    def setUpTestData(cls):
        # Create test tenant
        cls.tenant = Tenant.objects.create(
            name='API Test Store',
            subdomain='api-test',
        )
        # Create test branch
        cls.branch = Branch.objects.create(
            tenant=cls.tenant,
            name='API Test Branch',
            address='456 API Street',
        )
        # Create test user
        cls.user = User.objects.create_user(
            username='apiuser',
            password='apipass123',
            email='api@test.com'
        )
        cls.user_profile = UserProfile.objects.create(
            user=cls.user,
            tenant=cls.tenant,
            branch=cls.branch,
            role='admin'
        )
    
    def setUp(self):
        """Set up authenticated client for each test."""
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)


class AuthenticationAPITest(APITestMixin, APITestCase):
    """Tests for authentication endpoints."""
    
    def test_login_success(self):
        """Test successful JWT token authentication."""
        client = APIClient()
        url = reverse('token_obtain_pair')
        response = client.post(url, {
            'username': 'apiuser',
            'password': 'apipass123'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_login_failure(self):
        """Test failed authentication with wrong credentials."""
        client = APIClient()
        url = reverse('token_obtain_pair')
        response = client.post(url, {
            'username': 'apiuser',
            'password': 'wrongpassword'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_token_refresh(self):
        """Test JWT token refresh."""
        client = APIClient()
        # First, get tokens
        login_url = reverse('token_obtain_pair')
        login_response = client.post(login_url, {
            'username': 'apiuser',
            'password': 'apipass123'
        }, format='json')
        refresh_token = login_response.data['refresh']
        
        # Then, refresh the access token
        refresh_url = reverse('token_refresh')
        response = client.post(refresh_url, {
            'refresh': refresh_token
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_current_user_endpoint(self):
        """Test get current user details."""
        url = reverse('auth_user_details')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'apiuser')
    
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated requests are denied."""
        client = APIClient()  # No authentication
        url = reverse('product-list')
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProductAPITest(APITestMixin, APITestCase):
    """Tests for Product API endpoints."""
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.category = Category.objects.create(
            tenant=cls.tenant,
            branch=cls.branch,
            name='Test Category'
        )
        cls.product = Product.objects.create(
            tenant=cls.tenant,
            branch=cls.branch,
            category=cls.category,
            name='API Test Product',
            sku='API-001',
            price=Decimal('49.99'),
            cost_price=Decimal('25.00'),
            stock_quantity=50
        )
    
    def test_list_products(self):
        """Test listing all products."""
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Response may be paginated
        if 'results' in response.data:
            self.assertGreaterEqual(len(response.data['results']), 1)
        else:
            self.assertGreaterEqual(len(response.data), 1)
    
    def test_retrieve_product(self):
        """Test retrieving a single product."""
        url = reverse('product-detail', kwargs={'pk': self.product.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'API Test Product')
        self.assertEqual(response.data['sku'], 'API-001')
    
    def test_create_product(self):
        """Test creating a new product."""
        url = reverse('product-list')
        data = {
            'name': 'New API Product',
            'sku': 'API-002',
            'price': '99.99',
            'stock_quantity': 100,
            'category': str(self.category.pk)
        }
        response = self.client.post(url, data, format='json')
        # May be 201 or 200 depending on implementation
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])
    
    def test_update_product(self):
        """Test updating an existing product."""
        url = reverse('product-detail', kwargs={'pk': self.product.pk})
        data = {
            'name': 'Updated Product Name',
            'sku': self.product.sku,
            'price': '59.99',
            'stock_quantity': 75,
            'category': str(self.category.pk)
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Updated Product Name')
    
    def test_search_products(self):
        """Test searching products by name."""
        url = reverse('product-list')
        response = self.client.get(url, {'search': 'API Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CategoryAPITest(APITestMixin, APITestCase):
    """Tests for Category API endpoints."""
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.category = Category.objects.create(
            tenant=cls.tenant,
            branch=cls.branch,
            name='Electronics',
            description='Electronic items'
        )
    
    def test_list_categories(self):
        """Test listing all categories."""
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_retrieve_category(self):
        """Test retrieving a single category."""
        url = reverse('category-detail', kwargs={'pk': self.category.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Electronics')
    
    def test_create_category(self):
        """Test creating a new category."""
        url = reverse('category-list')
        data = {
            'name': 'Books',
            'description': 'Book items'
        }
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])


class CustomerAPITest(APITestMixin, APITestCase):
    """Tests for Customer API endpoints."""
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.customer = Customer.objects.create(
            tenant=cls.tenant,
            branch=cls.branch,
            name='API Customer',
            email='customer@api.test',
            phone='555-API-TEST',
            customer_type='retail'
        )
    
    def test_list_customers(self):
        """Test listing all customers."""
        url = reverse('customer-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_retrieve_customer(self):
        """Test retrieving a single customer."""
        url = reverse('customer-detail', kwargs={'pk': self.customer.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'API Customer')
    
    def test_create_customer(self):
        """Test creating a new customer."""
        url = reverse('customer-list')
        data = {
            'name': 'New Customer',
            'email': 'new@customer.test',
            'phone': '555-NEW-TEST',
            'customer_type': 'retail'
        }
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])
    
    def test_search_customers(self):
        """Test searching customers by name."""
        url = reverse('customer-list')
        response = self.client.get(url, {'search': 'API Customer'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class OrderAPITest(APITestMixin, APITestCase):
    """Tests for Order API endpoints."""
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.customer = Customer.objects.create(
            tenant=cls.tenant,
            name='Order Customer'
        )
        cls.category = Category.objects.create(
            tenant=cls.tenant,
            name='Order Category'
        )
        cls.product = Product.objects.create(
            tenant=cls.tenant,
            branch=cls.branch,
            category=cls.category,
            name='Order Product',
            sku='ORD-001',
            price=Decimal('25.00'),
            stock_quantity=100
        )
        cls.order = Order.objects.create(
            tenant=cls.tenant,
            branch=cls.branch,
            customer=cls.customer,
            cashier=cls.user_profile,
            subtotal=Decimal('50.00'),
            tax_amount=Decimal('5.00'),
            total_amount=Decimal('55.00'),
            payment_method='cash',
            status='completed'
        )
        cls.order_item = OrderItem.objects.create(
            order=cls.order,
            product=cls.product,
            quantity=2,
            price=Decimal('25.00'),
            cost_price=Decimal('15.00')
        )
    
    def test_list_orders(self):
        """Test listing all orders."""
        url = reverse('order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_retrieve_order(self):
        """Test retrieving a single order."""
        url = reverse('order-detail', kwargs={'pk': self.order.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_orders_by_status(self):
        """Test filtering orders by status."""
        url = reverse('order-list')
        response = self.client.get(url, {'status': 'completed'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_orders_by_payment_method(self):
        """Test filtering orders by payment method."""
        url = reverse('order-list')
        response = self.client.get(url, {'payment_method': 'cash'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
