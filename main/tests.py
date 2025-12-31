"""
Unit tests for core models in the main app.
Tests cover Product, Order, OrderItem, and Category models.
"""

from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import Tenant, Branch, UserProfile
from main.models import Product, Category, Order, OrderItem, Customer


class TenantTestMixin:
    """Mixin to set up tenant and branch for tests."""
    
    @classmethod
    def setUpTestData(cls):
        # Create a test tenant
        cls.tenant = Tenant.objects.create(
            name='Test Store',
            subdomain='test-store',
        )
        # Create a test branch
        cls.branch = Branch.objects.create(
            tenant=cls.tenant,
            name='Main Branch',
            address='123 Test Street',
        )
        # Create a test user
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        cls.user_profile = UserProfile.objects.create(
            user=cls.user,
            tenant=cls.tenant,
            branch=cls.branch,
            role='manager'
        )


class CategoryModelTest(TenantTestMixin, TestCase):
    """Tests for the Category model."""
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.category = Category.objects.create(
            tenant=cls.tenant,
            branch=cls.branch,
            name='Electronics',
            description='Electronic devices and accessories'
        )
    
    def test_category_str(self):
        """Test category string representation."""
        self.assertEqual(str(self.category), 'Electronics')
    
    def test_category_has_tenant(self):
        """Test that category is linked to tenant."""
        self.assertEqual(self.category.tenant, self.tenant)


class ProductModelTest(TenantTestMixin, TestCase):
    """Tests for the Product model."""
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.category = Category.objects.create(
            tenant=cls.tenant,
            name='Test Category'
        )
        cls.product = Product.objects.create(
            tenant=cls.tenant,
            branch=cls.branch,
            category=cls.category,
            name='Test Product',
            sku='TEST-001',
            price=Decimal('99.99'),
            cost_price=Decimal('50.00'),
            stock_quantity=100,
            low_stock_threshold=10
        )
    
    def test_product_str(self):
        """Test product string representation."""
        self.assertEqual(str(self.product), 'Test Product')
    
    def test_product_default_values(self):
        """Test product default field values."""
        self.assertTrue(self.product.is_active)
        self.assertFalse(self.product.has_variants)
        self.assertFalse(self.product.is_composite)
        self.assertFalse(self.product.auto_reorder)
    
    def test_product_price_fields(self):
        """Test product price fields."""
        self.assertEqual(self.product.price, Decimal('99.99'))
        self.assertEqual(self.product.cost_price, Decimal('50.00'))
        self.assertEqual(self.product.wholesale_price, Decimal('0.00'))
    
    def test_product_stock(self):
        """Test product stock fields."""
        self.assertEqual(self.product.stock_quantity, 100)
        self.assertEqual(self.product.low_stock_threshold, 10)
    
    def test_product_is_low_stock(self):
        """Test low stock detection."""
        # Product has 100 stock, threshold is 10 - not low
        self.assertFalse(self.product.stock_quantity <= self.product.low_stock_threshold)
        
        # Reduce stock below threshold
        self.product.stock_quantity = 5
        self.assertTrue(self.product.stock_quantity <= self.product.low_stock_threshold)


class OrderModelTest(TenantTestMixin, TestCase):
    """Tests for the Order model."""
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.customer = Customer.objects.create(
            tenant=cls.tenant,
            name='Test Customer',
            email='customer@test.com',
            phone='1234567890'
        )
        cls.order = Order.objects.create(
            tenant=cls.tenant,
            branch=cls.branch,
            customer=cls.customer,
            cashier=cls.user_profile,
            order_number='ORD-000001',
            subtotal=Decimal('100.00'),
            tax_amount=Decimal('10.00'),
            total_amount=Decimal('110.00'),
            amount_paid=Decimal('110.00'),
            payment_method='cash',
            status='completed'
        )
    
    def test_order_str_with_order_number(self):
        """Test order string representation with order number."""
        expected = f"ORD-000001 - {self.tenant.name}"
        self.assertEqual(str(self.order), expected)
    
    def test_order_default_status(self):
        """Test order default status is pending."""
        new_order = Order.objects.create(
            tenant=self.tenant,
            branch=self.branch,
            total_amount=Decimal('50.00')
        )
        self.assertEqual(new_order.status, 'pending')
    
    def test_order_payment_methods(self):
        """Test valid payment methods."""
        valid_methods = ['cash', 'card', 'mobile', 'gift_card', 'store_credit']
        for method in valid_methods:
            self.order.payment_method = method
            self.order.save()
            self.assertEqual(self.order.payment_method, method)
    
    def test_order_status_choices(self):
        """Test valid order statuses."""
        valid_statuses = ['pending', 'completed', 'cancelled']
        for status in valid_statuses:
            self.order.status = status
            self.order.save()
            self.assertEqual(self.order.status, status)
    
    def test_order_financial_fields(self):
        """Test order financial calculations."""
        self.assertEqual(self.order.subtotal, Decimal('100.00'))
        self.assertEqual(self.order.tax_amount, Decimal('10.00'))
        self.assertEqual(self.order.total_amount, Decimal('110.00'))
        # Verify: subtotal + tax = total
        calculated_total = self.order.subtotal + self.order.tax_amount
        self.assertEqual(calculated_total, self.order.total_amount)


class OrderItemModelTest(TenantTestMixin, TestCase):
    """Tests for the OrderItem model."""
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.product = Product.objects.create(
            tenant=cls.tenant,
            branch=cls.branch,
            name='Test Product',
            sku='TEST-001',
            price=Decimal('25.00'),
            cost_price=Decimal('15.00'),
            stock_quantity=50
        )
        cls.order = Order.objects.create(
            tenant=cls.tenant,
            branch=cls.branch,
            total_amount=Decimal('75.00'),
            status='pending'
        )
        cls.order_item = OrderItem.objects.create(
            order=cls.order,
            product=cls.product,
            item_number='ITM-00001',
            quantity=3,
            price=Decimal('25.00'),
            cost_price=Decimal('15.00')
        )
    
    def test_order_item_str_with_item_number(self):
        """Test order item string representation with item number."""
        expected = "ITM-00001 - 3 x Test Product"
        self.assertEqual(str(self.order_item), expected)
    
    def test_order_item_total_price(self):
        """Test order item total price calculation."""
        # quantity (3) * price (25.00) = 75.00
        expected_total = Decimal('75.00')
        self.assertEqual(self.order_item.get_total_item_price(), expected_total)
    
    def test_order_item_profit_calculation(self):
        """Test order item profit calculation."""
        # Revenue per item: 25.00
        # Cost per item: 15.00
        # Profit per item: 10.00
        # Total profit for 3 items: 30.00
        total_revenue = self.order_item.quantity * self.order_item.price
        total_cost = self.order_item.quantity * self.order_item.cost_price
        profit = total_revenue - total_cost
        self.assertEqual(profit, Decimal('30.00'))
    
    def test_order_item_links_to_order(self):
        """Test order item is linked to order."""
        self.assertEqual(self.order_item.order, self.order)
        self.assertIn(self.order_item, self.order.items.all())
    
    def test_order_item_links_to_product(self):
        """Test order item is linked to product."""
        self.assertEqual(self.order_item.product, self.product)


class CustomerModelTest(TenantTestMixin, TestCase):
    """Tests for the Customer model."""
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.customer = Customer.objects.create(
            tenant=cls.tenant,
            name='John Doe',
            email='john@example.com',
            phone='555-1234',
            customer_type='retail'
        )
    
    def test_customer_str(self):
        """Test customer string representation."""
        self.assertEqual(str(self.customer), 'John Doe')
    
    def test_customer_default_type(self):
        """Test customer default type is retail."""
        new_customer = Customer.objects.create(
            tenant=self.tenant,
            name='Jane Doe'
        )
        self.assertEqual(new_customer.customer_type, 'retail')
    
    def test_customer_types(self):
        """Test valid customer types."""
        self.customer.customer_type = 'wholesale'
        self.customer.save()
        self.assertEqual(self.customer.customer_type, 'wholesale')
