import uuid
from django_tenants.test.cases import TenantTestCase
from django.contrib.auth.models import User
from accounts.models import Tenant, Branch, UserProfile
from main.models import Product, Category, Order, ProductComponent
from branches.services.pos import POSService

class SyncLifecycleTests(TenantTestCase):
    def setUp(self):
        super().setUp()
        # TenantTestCase automatically creates self.tenant
        self.branch = Branch.objects.create(tenant=self.tenant, name="Test Branch")
        self.user = User.objects.create_user(username="testuser", password="password")
        self.profile = UserProfile.objects.create(user=self.user, tenant=self.tenant, branch=self.branch, role='admin')
        
        self.pos_service = POSService(tenant=self.tenant, user_profile=self.profile)
        
        self.category = Category.objects.create(tenant=self.tenant, branch=self.branch, name="General")
        
        # Create products
        self.product_a = Product.objects.create(
            tenant=self.tenant, branch=self.branch, category=self.category,
            name="Product A", sku="SKU-A", price=100.00, stock_quantity=50
        )
        self.component_1 = Product.objects.create(
            tenant=self.tenant, branch=self.branch, category=self.category,
            name="Comp 1", sku="SKU-C1", price=10.00, stock_quantity=100
        )
        self.bundle = Product.objects.create(
            tenant=self.tenant, branch=self.branch, category=self.category,
            name="Bundle", sku="SKU-B", price=150.00, stock_quantity=0,
            is_composite=True # Bundle depends on components
        )
        
        ProductComponent.objects.create(
            parent_product=self.bundle,
            component_product=self.component_1,
            quantity=2
        )

    def test_sync_order_basic(self):
        """Test basic order synchronization with stock deduction"""
        order_uuid = str(uuid.uuid4())
        data = {
            'branch_id': str(self.branch.id),
            'total_amount': 200.00,
            'payment_method': 'cash',
            'items': [
                {
                    'id': str(self.product_a.id),
                    'quantity': 2,
                    'price': 100.00
                }
            ]
        }
        
        result = self.pos_service.sync_order(order_uuid, data)
        self.assertEqual(result['status'], 'success', result.get('message'))
        
        # Verify order created
        order = Order.objects.get(offline_uuid=order_uuid)
        self.assertEqual(order.total_amount, 200.00)
        self.assertEqual(order.items.count(), 1)
        
        # Verify stock deducted
        self.product_a.refresh_from_db()
        self.assertEqual(self.product_a.stock_quantity, 48)

    def test_sync_order_composite(self):
        """Test order synchronization for composite products (bundles)"""
        order_uuid = str(uuid.uuid4())
        data = {
            'branch_id': str(self.branch.id),
            'total_amount': 150.00,
            'payment_method': 'cash',
            'items': [
                {
                    'id': str(self.bundle.id),
                    'quantity': 1,
                    'price': 150.00
                }
            ]
        }
        
        result = self.pos_service.sync_order(order_uuid, data)
        self.assertEqual(result['status'], 'success', result.get('message'))
        
        # Verify component stock deducted
        self.component_1.refresh_from_db()
        # 100 - (1 bundle * 2 components) = 98
        self.assertEqual(self.component_1.stock_quantity, 98)

    def test_sync_order_duplicate(self):
        """Test that duplicate sync requests are handled gracefully"""
        order_uuid = str(uuid.uuid4())
        data = {
            'branch_id': str(self.branch.id),
            'total_amount': 100.00,
            'payment_method': 'cash',
            'items': [{'id': str(self.product_a.id), 'quantity': 1, 'price': 100.00}]
        }
        
        # First sync
        res1 = self.pos_service.sync_order(order_uuid, data)
        self.assertEqual(res1['status'], 'success')
        initial_order_count = Order.objects.count()
        
        # Second sync with same UUID
        res2 = self.pos_service.sync_order(order_uuid, data)
        self.assertEqual(res2['status'], 'already_synced')
        self.assertEqual(Order.objects.count(), initial_order_count)

    def test_create_transfer(self):
        """Test stock transfer creation and deduction"""
        # Create another branch
        branch_b = Branch.objects.create(tenant=self.tenant, name="Branch B")
        
        data = {
            'source_branch_id': str(self.branch.id),
            'destination_branch_id': str(branch_b.id),
            'items': [
                {
                    'product_id': str(self.product_a.id),
                    'quantity': 10
                }
            ]
        }
        
        result = self.pos_service.create_transfer(data)
        self.assertEqual(result['status'], 'success', result.get('message'))
        
        # Verify stock deducted from source
        self.product_a.refresh_from_db()
        self.assertEqual(self.product_a.stock_quantity, 40)
