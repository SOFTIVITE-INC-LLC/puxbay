from rest_framework import serializers
from main.models import (
    Category, Product, ProductVariant, Customer, Order, OrderItem,
    ProductComponent, ProductHistory, CustomerFeedback, GiftCard, 
    Return, ReturnItem, Expense, ExpenseCategory, PaymentMethod,
    CustomerTier, LoyaltyTransaction, StoreCreditTransaction, TaxConfiguration
)
from accounts.models import Tenant, Branch, UserProfile
from .models import (
    Supplier, PurchaseOrder, PurchaseOrderItem, 
    StockTransfer, StockTransferItem, 
    StocktakeSession, StocktakeEntry,
    CashDrawerSession
)
from notifications.models import Notification, NotificationSetting

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'name', 'sku', 'price', 'stock_quantity', 'attributes', 'is_active']

class ProductComponentSerializer(serializers.ModelSerializer):
    component_name = serializers.CharField(source='component_product.name', read_only=True)
    component_sku = serializers.CharField(source='component_product.sku', read_only=True)
    
    class Meta:
        model = ProductComponent
        fields = ['id', 'component_product', 'component_name', 'component_sku', 'quantity']

class ProductHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source='changed_by.user.username', read_only=True)
    
    class Meta:
        model = ProductHistory
        fields = ['id', 'action', 'changed_by', 'changed_by_name', 'changed_at', 'changes_summary']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    components = ProductComponentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'price', 'stock_quantity', 'description', 'image', 
            'category', 'category_name', 'variants', 'low_stock_threshold', 
            'cost_price', 'expiry_date', 'barcode', 'is_active',
            'minimum_wholesale_quantity', 'is_composite', 'components',
            'metadata', 'created_at', 'updated_at'
        ]

class CustomerSerializer(serializers.ModelSerializer):
    tier_name = serializers.CharField(source='tier.name', read_only=True)
    
    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'email', 'phone', 'address', 'customer_type', 
            'loyalty_points', 'store_credit_balance', 'total_spend', 
            'tier', 'tier_name', 'marketing_opt_in', 'metadata', 'created_at'
        ]

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    sku = serializers.CharField(source='product.sku', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'sku', 'item_number', 
            'quantity', 'price', 'cost_price', 'get_total_item_price'
        ]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    cashier_name = serializers.CharField(source='cashier.user.username', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'created_at', 'updated_at',
            'subtotal', 'tax_amount', 'total_amount', 'amount_paid',
            'payment_method', 'ordering_type', 'offline_uuid',
            'customer', 'customer_name', 'cashier', 'cashier_name',
            'branch', 'branch_name', 'items', 'metadata'
        ]

class OrderCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating orders"""
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        help_text="List of items: [{'product_id': 'uuid', 'quantity': 1, 'price': 10.00}]"
    )
    
    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'branch', 'subtotal', 'tax_amount', 
            'total_amount', 'amount_paid', 'payment_method', 
            'ordering_type', 'items', 'offline_uuid'
        ]
        
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        # Tenant is already set in perform_create of viewset
        order = Order.objects.create(**validated_data)
        
        for item in items_data:
            # Handle product fetching safely
            try:
                product = Product.objects.get(id=item['product_id'])
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price=item.get('price', product.price),
                    cost_price=product.cost_price
                )
            except Product.DoesNotExist:
                continue # Skip invalid products (or raise validation error)
                
        return order

# -----------------------------------------------------------------------------
# Supply Chain Serializers
# -----------------------------------------------------------------------------

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'contact_person', 'email', 'phone', 'address', 'created_at']

class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    sku = serializers.CharField(source='product.sku', read_only=True)
    
    class Meta:
        model = PurchaseOrderItem
        fields = ['id', 'product', 'product_name', 'sku', 'quantity', 'unit_cost']

class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.user.username', read_only=True)
    
    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'reference_id', 'status', 'supplier', 'supplier_name', 
            'branch', 'branch_name', 'total_cost', 'expected_date', 
            'notes', 'created_by', 'created_by_name', 'created_at', 'items'
        ]

class StockTransferItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = StockTransferItem
        fields = ['id', 'product', 'product_name', 'quantity', 'transfer_price']

class StockTransferSerializer(serializers.ModelSerializer):
    items = StockTransferItemSerializer(many=True, read_only=True)
    source_branch_name = serializers.CharField(source='source_branch.name', read_only=True)
    destination_branch_name = serializers.CharField(source='destination_branch.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.user.username', read_only=True)
    
    class Meta:
        model = StockTransfer
        fields = [
            'id', 'reference_id', 'status', 'source_branch', 'source_branch_name', 
            'destination_branch', 'destination_branch_name', 'notes', 
            'created_by', 'created_by_name', 'created_at', 'completed_at', 'items'
        ]

# -----------------------------------------------------------------------------
# Store Operations Serializers
# -----------------------------------------------------------------------------

class StocktakeEntrySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    sku = serializers.CharField(source='product.sku', read_only=True)
    difference = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = StocktakeEntry
        fields = [
            'id', 'product', 'product_name', 'sku', 'counted_quantity', 
            'expected_quantity', 'difference', 'notes', 'updated_at'
        ]

class StocktakeSessionSerializer(serializers.ModelSerializer):
    entries = StocktakeEntrySerializer(many=True, read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.user.username', read_only=True)
    
    class Meta:
        model = StocktakeSession
        fields = [
            'id', 'branch', 'branch_name', 'status', 'notes', 
            'created_by', 'created_by_name', 'started_at', 'completed_at', 'entries'
        ]

class CashDrawerSessionSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    employee_name = serializers.CharField(source='employee.user.username', read_only=True)
    
    class Meta:
        model = CashDrawerSession
class CashDrawerSessionSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    employee_name = serializers.CharField(source='employee.user.username', read_only=True)
    
    class Meta:
        model = CashDrawerSession
        fields = [
            'id', 'branch', 'branch_name', 'employee', 'employee_name',
            'status', 'start_time', 'end_time', 'starting_balance', 
            'expected_cash', 'actual_cash', 'difference', 'notes'
        ]

# -----------------------------------------------------------------------------
# Notifications & CRM Serializers
# -----------------------------------------------------------------------------

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'notification_type', 'category', 'is_read', 'created_at']

class CustomerFeedbackSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    
    class Meta:
        model = CustomerFeedback
        fields = ['id', 'customer', 'customer_name', 'transaction', 'rating', 'comment', 'created_at']

class GiftCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiftCard
        fields = ['id', 'code', 'balance', 'status', 'expiry_date']

class CustomerTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerTier
        fields = ['id', 'name', 'min_spend', 'discount_percentage', 'color', 'icon']

class LoyaltyTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoyaltyTransaction
        fields = ['id', 'customer', 'order', 'points', 'transaction_type', 'description', 'created_at']

class StoreCreditTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreCreditTransaction
        fields = ['id', 'customer', 'amount', 'reference', 'created_at']

# -----------------------------------------------------------------------------
# Returns & Financial Serializers
# -----------------------------------------------------------------------------

class ReturnItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = ReturnItem
        fields = ['id', 'product', 'product_name', 'quantity', 'condition', 'restock', 'unit_price']

class ReturnSerializer(serializers.ModelSerializer):
    items = ReturnItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = Return
        fields = [
            'id', 'order', 'order_number', 'customer', 'customer_name', 
            'reason', 'reason_detail', 'status', 'refund_method', 
            'refund_amount', 'created_at', 'items'
        ]

class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = ['id', 'name', 'type']

class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.user.username', read_only=True)
    
    class Meta:
        model = Expense
        fields = [
            'id', 'category', 'category_name', 'amount', 'date', 
            'description', 'receipt_file', 'created_by', 'created_by_name', 'created_at'
        ]

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['id', 'name', 'provider', 'is_active']

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = [
            'id', 'name', 'unique_id', 'address', 'phone', 
            'branch_type', 'currency_code', 'currency_symbol',
            'low_stock_threshold', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class TaxConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxConfiguration
        fields = [
            'id', 'tax_type', 'tax_rate', 'tax_number', 
            'include_tax_in_prices', 'is_active', 'updated_at'
        ]
        read_only_fields = ['id', 'updated_at']

class StaffSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'full_name', 'email', 'role', 'branch', 'branch_name']
