from django.db import models
from django.contrib.auth.models import User
from accounts.models import Branch, Tenant, UserProfile
import uuid
from utils.encryption import EncryptedTextField
import datetime

class Supplier(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='suppliers')
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = EncryptedTextField(blank=True, null=True)
    address = EncryptedTextField(blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True)
    
    # Financial Default
    payment_terms = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., Net 30, Due on Receipt")
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Maximum amount we can owe this supplier")
    outstanding_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Current amount we owe this supplier")
    
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class SupplierProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='supplier_link')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='portal_users')

    def __str__(self):
        return f"{self.user_profile.user.username} -> {self.supplier.name}"

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.DO_NOTHING, related_name='categories')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='categories', null=True, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.DO_NOTHING, related_name='products')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, db_index=True) # Stock Keeping Unit
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    
    # Extended Details
    expiry_date = models.DateField(blank=True, null=True)
    barcode = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    batch_number = models.CharField(max_length=100, blank=True, null=True)
    invoice_waybill_number = models.CharField(max_length=100, blank=True, null=True, help_text="Invoice or Waybill number")
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    low_stock_threshold = models.PositiveIntegerField(default=10)
    
    # Origin and Manufacturing Information
    country_of_origin = models.CharField(max_length=100, blank=True, null=True, help_text="Country where product was manufactured")
    manufacturer_name = models.CharField(max_length=200, blank=True, null=True, help_text="Name of manufacturer")
    manufacturer_address = models.TextField(blank=True, null=True, help_text="Manufacturer's address")
    manufacturing_date = models.DateField(blank=True, null=True, help_text="Date of manufacture")
    
    # Wholesale Fields
    wholesale_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    minimum_wholesale_quantity = models.PositiveIntegerField(default=1, help_text="Minimum quantity for wholesale price to apply")
    
    # Inventory Settings
    is_batch_tracked = models.BooleanField(default=False, help_text="Enable for expiry, serial, or batch tracking")
    auto_reorder = models.BooleanField(default=False, help_text="Automatically generate PO when stock is low")
    reorder_quantity = models.PositiveIntegerField(default=10, help_text="Quantity to reorder automatically")
    low_stock_threshold = models.IntegerField(default=10, help_text="Alert when stock falls below this level")
    alert_enabled = models.BooleanField(default=True, help_text="Enable low stock alerts for this product")
    
    is_active = models.BooleanField(default=True, db_index=True)
    has_variants = models.BooleanField(default=False, help_text="Does this product have variations (e.g. Size, Color)?")
    is_composite = models.BooleanField(default=False, help_text="Is this product a bundle/composite of other products?")
    metadata = models.JSONField(default=dict, blank=True, help_text="Custom JSON metadata for developers")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def image_url(self):
        from django.templatetags.static import static
        if self.image:
            try:
                return self.image.url
            except (ValueError, AttributeError):
                pass
        return static('images/default_product.png')

    def __str__(self):
        return self.name

    def get_daily_sales_velocity(self, days=30):
        """Calculate average quantity sold per day over the last N days"""
        from django.db.models import Sum, Q, F
        from django.utils import timezone
        import datetime
        
        start_date = timezone.now() - datetime.timedelta(days=days)
        
        # Aggregate quantity from OrderItems where order is completed
        total_sold = self.order_items.filter(
            order__created_at__gte=start_date,
            order__status='completed'
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        if total_sold == 0:
            return 0.0
            
        return float(total_sold) / days

    def get_days_until_stockout(self):
        """Predict days until stock runs out based on 30-day velocity"""
        velocity = self.get_daily_sales_velocity(days=30)
        if velocity <= 0:
            return 999 # Technically infinite, but we return a high number
        
        days_left = self.stock_quantity / velocity
        return round(days_left, 1)

class ProductComponent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='components')
    component_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='included_in_bundles')
    quantity = models.PositiveIntegerField(default=1, help_text="Quantity of component in the bundle")
    
    class Meta:
        unique_together = ('parent_product', 'component_product')
        
    def __str__(self):
        return f"{self.quantity} x {self.component_product.name} in {self.parent_product.name}"

class ProductHistory(models.Model):
    """Track all changes to products for audit trail and revert functionality"""
    ACTION_CHOICES = (
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('deleted', 'Deleted'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='history')
    product_id_snapshot = models.UUIDField(help_text="Original product ID (preserved even if product is deleted)")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    # Changed to DO_NOTHING prevents Public Schema crash when deleting UserProfile
    changed_by = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='product_changes')
    changed_at = models.DateTimeField(auto_now_add=True)
    snapshot_data = models.JSONField(help_text="Complete product data snapshot at time of change")
    changes_summary = models.TextField(blank=True, help_text="Human-readable summary of changes")
    tenant = models.ForeignKey(Tenant, on_delete=models.DO_NOTHING, related_name='product_history')
    
    class Meta:
        ordering = ['-changed_at']
        verbose_name = "Product History"
        verbose_name_plural = "Product History"
        indexes = [
            models.Index(fields=['product_id_snapshot', '-changed_at']),
            models.Index(fields=['action', '-changed_at']),
            models.Index(fields=['tenant', '-changed_at']),
        ]
    
    def __str__(self):
        product_name = self.snapshot_data.get('name', 'Unknown Product')
        user_name = self.changed_by.user.username if self.changed_by else 'System'
        return f"{product_name} - {self.get_action_display()} by {user_name}"
    
    def get_field_changes(self):
        """Extract specific field changes from snapshot data"""
        if self.action == 'created':
            return "Product created"
        elif self.action == 'deleted':
            return "Product deleted"
        return self.changes_summary


class ProductVariant(models.Model):
    """Specific variation of a product (e.g. Red/Large)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100, help_text="Variant name, e.g. 'Red / Large'")
    sku = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Override base product price")
    stock_quantity = models.PositiveIntegerField(default=0)
    attributes = models.JSONField(default=dict, blank=True, help_text="Key-value pairs, e.g. {'Color': 'Red', 'Size': 'L'}")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.name}"

    def get_price(self):
        """Return variant price if set, otherwise product price"""
        return self.price if self.price is not None else self.product.price

class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='customer_profiles')
    CUSTOMER_TYPES = [
        ('retail', 'Retail'),
        ('wholesale', 'Wholesale'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.DO_NOTHING, related_name='customers')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='customers', null=True, blank=True)
    tier = models.ForeignKey('CustomerTier', on_delete=models.SET_NULL, null=True, blank=True, related_name='customers')
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = EncryptedTextField(blank=True, null=True)
    address = EncryptedTextField(blank=True, null=True)
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPES, default='retail')
    
    # CRM Fields
    loyalty_points = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    store_credit_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_spend = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Total lifetime spend")
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Maximum amount this customer can owe us")
    outstanding_debt = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Current amount this customer owes us")
    total_orders = models.PositiveIntegerField(default=0)
    last_purchase_at = models.DateTimeField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    marketing_opt_in = models.BooleanField(default=True)
    
    # Email Verification
    is_email_verified = models.BooleanField(default=False, help_text="Whether the customer's email has been verified")
    email_verification_token = models.UUIDField(default=uuid.uuid4, editable=False, help_text="Token for email verification")
    
    metadata = models.JSONField(default=dict, blank=True, help_text="Custom JSON metadata for developers")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['tenant', 'name']),
            models.Index(fields=['tenant', '-outstanding_debt']),
            models.Index(fields=['tenant', '-loyalty_points']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return self.name

    def calculate_tier(self):
        """Check and update customer tier based on total spend"""
        # Find the highest tier where min_spend <= total_spend
        eligible_tier = CustomerTier.objects.filter(
            tenant=self.tenant, 
            min_spend__lte=self.total_spend
        ).order_by('-min_spend').first()
        
        if eligible_tier and self.tier != eligible_tier:
            self.tier = eligible_tier
            self.save(update_fields=['tier'])
            return True
        return False

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('ready', 'Ready'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('mobile', 'Mobile Money'),
        ('gift_card', 'Gift Card'),
        ('store_credit', 'Store Credit'),
        ('loyalty_points', 'Loyalty Points'),
        ('stripe', 'Stripe'),
        ('paystack', 'Paystack'),
        ('credit', 'On Credit / Account'),
        ('split', 'Split Payment'),
    )
    
    tenant = models.ForeignKey(Tenant, on_delete=models.DO_NOTHING, related_name='orders')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    cashier = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_orders')
    
    # Unique identifier
    order_number = EncryptedTextField(max_length=30, unique=True, db_index=True, blank=True, null=True, help_text="Human-readable order number (e.g., ORD-000001)")
    
    # Financial fields
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Amount before tax")
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Tax amount")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Subtotal + Tax")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Amount actually paid")
    
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    ordering_type = models.CharField(max_length=20, choices=(('pos', 'Point of Sale'), ('online', 'Online Store'), ('kiosk', 'Kiosk / Self-Checkout')), default='pos')
    payment_reference = models.CharField(max_length=255, blank=True, null=True, db_index=True, help_text="Reference ID from external payment gateways (Stripe, Paystack, etc.)")
    offline_uuid = models.CharField(max_length=36, blank=True, null=True, unique=True, db_index=True)  # For offline sync
    metadata = models.JSONField(default=dict, blank=True, help_text="Custom JSON metadata for developers")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            from utils.identifier_generator import generate_order_number
            self.order_number = generate_order_number(self.tenant)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.order_number:
            return f"{self.order_number} - {self.tenant.name}"
        return f"Order #{self.id} - {self.tenant.name}"

class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='order_items')
    item_number = EncryptedTextField(max_length=30, unique=True, db_index=True, blank=True, null=True, help_text="Human-readable item number (e.g., ITM-00001)")
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2) # Snapshot of price at time of order
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # Snapshot of cost at time of order

    def save(self, *args, **kwargs):
        if not self.item_number:
            from utils.identifier_generator import generate_item_number
            self.item_number = generate_item_number(self.order)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.item_number:
            product_name = self.product.name if self.product else 'Unknown Product'
            return f"{self.item_number} - {self.quantity} x {product_name}"
        return f"{self.quantity} x {self.product.name if self.product else 'Unknown Product'}"

    def get_total_item_price(self):
        return self.quantity * self.price



# -----------------------------------------------------------------------------
# CRM MODELS
# -----------------------------------------------------------------------------

class GiftCard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('expired', 'Expired'),
    )
    
    tenant = models.ForeignKey(Tenant, on_delete=models.DO_NOTHING, related_name='gift_cards')
    code = models.CharField(max_length=50, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    expiry_date = models.DateField(blank=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='gift_cards')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.code} - {self.balance}"

class LoyaltyTransaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    TRANSACTION_TYPES = (
        ('earn', 'Earned'),
        ('redeem', 'Redeemed'),
        ('adjustment', 'Adjustment'),
    )
    
    tenant = models.ForeignKey(Tenant, on_delete=models.DO_NOTHING)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loyalty_transactions')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    points = models.DecimalField(max_digits=10, decimal_places=2) # Can be negative for redemption
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    description = EncryptedTextField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.customer.name} - {self.points} ({self.transaction_type})"

class StoreCreditTransaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.DO_NOTHING)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='store_credit_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2) # Positive (credit) or Negative (debit)
    reference = models.CharField(max_length=255, help_text="Order ID or reason")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.customer.name} - {self.amount}"

class CRMSettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.OneToOneField(Tenant, on_delete=models.DO_NOTHING, related_name='crm_settings')
    points_per_currency = models.DecimalField(max_digits=5, decimal_places=2, default=1.00, help_text="Points earned per 1 unit of currency")
    redemption_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.01, help_text="Currency value of 1 point (e.g., 0.01 means 100 points = $1)")
    
    def __str__(self):
        return f"CRM Settings - {self.tenant.name}"

class CustomerTier(models.Model):
    """Customer Loyalty Tiers"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.DO_NOTHING, related_name='customer_tiers')
    name = models.CharField(max_length=50) # e.g., Silver, Gold, Platinum
    min_spend = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    color = models.CharField(max_length=20, default='blue', help_text="Tailwind color name e.g. blue, gold, purple")
    icon = models.CharField(max_length=50, default='star', help_text="Icon name")
    
    class Meta:
        ordering = ['min_spend']
        unique_together = ('tenant', 'name')

    def __str__(self):
        return f"{self.name} (> ${self.min_spend})"

class MarketingCampaign(models.Model):
    """Email and SMS Campaigns"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    TYPE_CHOICES = (
        ('email', 'Email'),
        ('sms', 'SMS'),
    )
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sent', 'Sent'),
        ('cancelled', 'Cancelled'),
    )
    TRIGGER_CHOICES = (
        ('manual', 'Manual One-time'),
        ('birthday', 'Customer Birthday'),
        ('inactive_30d', '30 Days Inactive'),
        ('first_purchase', 'After First Purchase'),
        ('tier_up', 'On Tier Upgrade'),
    )

    tenant = models.ForeignKey(Tenant, on_delete=models.DO_NOTHING, related_name='campaigns')
    name = models.CharField(max_length=100)
    campaign_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='email')
    subject = models.CharField(max_length=255, blank=True, help_text="Email subject or SMS header")
    message = EncryptedTextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    target_tier = models.ForeignKey(CustomerTier, on_delete=models.SET_NULL, null=True, blank=True, help_text="Leave blank to send to all customers")
    
    is_automated = models.BooleanField(default=False)
    trigger_event = models.CharField(max_length=30, choices=TRIGGER_CHOICES, default='manual')
    
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    last_run_at = models.DateTimeField(null=True, blank=True, help_text="Last time automation was checked/run")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

class CustomerFeedback(models.Model):
    """Customer Ratings and Feedback"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.DO_NOTHING, related_name='feedback')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='feedback')
    transaction = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedback')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    comment = EncryptedTextField(blank=True)
    is_public = models.BooleanField(default=False, help_text="Show in testimonials?")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer.name} - {self.rating}/5"

# -----------------------------------------------------------------------------
# FINANCIAL MANAGEMENT MODELS
# -----------------------------------------------------------------------------

class ExpenseCategory(models.Model):
    """Categories for organizing expenses"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    EXPENSE_TYPES = (
        ('fixed', 'Fixed'),
        ('variable', 'Variable'),
    )
    
    tenant = models.ForeignKey(Tenant, on_delete=models.DO_NOTHING, related_name='expense_categories')
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=EXPENSE_TYPES, default='variable')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Expense Categories"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

class Expense(models.Model):
    """Track operational expenses"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.DO_NOTHING, related_name='expenses')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='expenses', null=True, blank=True, help_text="Leave blank for company-wide expenses")
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT, related_name='expenses')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = EncryptedTextField()
    receipt_file = models.FileField(upload_to='expense_receipts/', blank=True, null=True)
    created_by = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, null=True, related_name='created_expenses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        branch_name = self.branch.name if self.branch else "Company-wide"
        return f"{self.category.name} - ${self.amount} ({branch_name})"

class PaymentMethod(models.Model):
    """Payment gateway configurations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    PROVIDER_CHOICES = (
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('cash', 'Cash'),
        ('card', 'Card Terminal'),
        ('mobile', 'Mobile Money'),
    )
    
    tenant = models.ForeignKey(Tenant, on_delete=models.DO_NOTHING, related_name='payment_methods')
    name = models.CharField(max_length=100)
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    is_active = models.BooleanField(default=True)
    # Note: Sensitive keys should be stored in environment variables, not database
    # These fields are for reference/display purposes only
    api_key_hint = models.CharField(max_length=50, blank=True, help_text="Last 4 characters of API key")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_provider_display()})"

class Payment(models.Model):
    """Track payment transactions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
    )
    
    tenant = models.ForeignKey(Tenant, on_delete=models.DO_NOTHING, related_name='payments')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=255, blank=True, null=True, help_text="External payment gateway transaction ID")
    metadata = models.JSONField(blank=True, null=True, help_text="Store payment gateway response data")
    error_message = EncryptedTextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment #{self.id} - {self.order} - ${self.amount} ({self.status})"

class Return(models.Model):
    """Track product returns and refund requests"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    REASON_CHOICES = (
        ('defective', 'Defective/Damaged'),
        ('wrong_item', 'Wrong Item'),
        ('changed_mind', 'Changed Mind'),
        ('not_as_described', 'Not As Described'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )
    
    REFUND_METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('card', 'Card Refund'),
        ('store_credit', 'Store Credit'),
        ('original', 'Original Payment Method'),
    )
    
    tenant = models.ForeignKey(Tenant, on_delete=models.DO_NOTHING, related_name='returns')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='returns')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='returns')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='returns')
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    reason_detail = EncryptedTextField(help_text="Detailed explanation of the return reason")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    refund_method = models.CharField(max_length=20, choices=REFUND_METHOD_CHOICES, default='original')
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    restocking_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_by = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, null=True, related_name='created_returns')
    approved_by = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='approved_returns')
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Return #{self.id} - Order #{self.order.id} - {self.get_status_display()}"
    
    def get_net_refund(self):
        """Calculate net refund after restocking fee"""
        return self.refund_amount - self.restocking_fee

class ReturnItem(models.Model):
    """Individual items in a return request"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CONDITION_CHOICES = (
        ('unopened', 'Unopened/Sealed'),
        ('opened', 'Opened'),
        ('damaged', 'Damaged'),
    )
    
    return_request = models.ForeignKey(Return, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='return_items')
    quantity = models.PositiveIntegerField(default=1)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='opened')
    restock = models.BooleanField(default=False, help_text="Whether to return this item to inventory")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price at time of original purchase")
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name if self.product else 'Unknown Product'}"
    
    def get_total_value(self):
        """Calculate total value of returned items"""
        return self.quantity * self.unit_price

class TaxConfiguration(models.Model):
    """Tax settings for calculating VAT/Sales Tax"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    TAX_TYPE_CHOICES = (
        ('vat', 'VAT (Value Added Tax)'),
        ('sales_tax', 'Sales Tax'),
        ('gst', 'GST (Goods and Services Tax)'),
        ('none', 'No Tax'),
    )
    
    tenant = models.OneToOneField(Tenant, on_delete=models.DO_NOTHING, related_name='tax_config')
    tax_type = models.CharField(max_length=20, choices=TAX_TYPE_CHOICES, default='sales_tax')
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Tax rate as percentage (e.g., 15.00 for 15%)")
    tax_number = models.CharField(max_length=50, blank=True, null=True, help_text="Tax registration number")
    include_tax_in_prices = models.BooleanField(default=False, help_text="Whether displayed prices include tax")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Tax Configuration"
        verbose_name_plural = "Tax Configurations"
    
    def __str__(self):
        return f"{self.tenant.name} - {self.get_tax_type_display()} ({self.tax_rate}%)"
    
    def calculate_tax(self, amount):
        """Calculate tax amount for a given subtotal"""
        if not self.is_active:
            return 0
        return (amount * self.tax_rate) / 100


class StockAlert(models.Model):
    """Track low stock and out of stock alerts."""
    ALERT_TYPES = (
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    threshold = models.IntegerField(help_text="Threshold at time of alert")
    current_stock = models.IntegerField(help_text="Stock level at time of alert")
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    notified = models.BooleanField(default=False, help_text="Email notification sent")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_resolved', 'created_at']),
            models.Index(fields=['product', 'is_resolved']),
        ]
    
    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.product.name} ({self.current_stock} units)"
    
    def resolve(self):
        """Mark alert as resolved."""
        from django.utils import timezone
        self.is_resolved = True
        self.resolved_at = timezone.now()
        self.save()


class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=5)
    exchange_rate = models.DecimalField(max_digits=20, decimal_places=6, default=1.0, help_text="Rate relative to base currency (USD)")
    is_active = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Currencies"

    def __str__(self):
        return f"{self.code} ({self.symbol}) - {self.exchange_rate}"



class CustomerCreditTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('purchase', 'Credit Purchase'),
        ('payment', 'Payment Received'),
        ('adjustment', 'Adjustment'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='credit_transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2) # Positive for debt increase, Negative for payment
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    reference = models.CharField(max_length=100, blank=True, help_text="Order ID or Payment Ref")
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer.name} - {self.transaction_type} - {self.amount}"

class SupplierCreditTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('purchase', 'Credit Purchase (PO)'),
        ('payment', 'Payment Made'),
        ('adjustment', 'Adjustment'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='credit_transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2) # Positive for balance increase, Negative for payment
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    reference = models.CharField(max_length=100, blank=True, help_text="PO ID or Payment Ref")
    receipt_image = models.ImageField(upload_to='supplier_payments/', blank=True, null=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.supplier.name} - {self.transaction_type} - {self.amount}"

class DatabaseBackup(models.Model):
    filename = models.CharField(max_length=255, unique=True)
    file_path = models.CharField(max_length=512)
    size_bytes = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        permissions = [
            ("can_download_backup", "Can download database backups"),
        ]

    def __str__(self):
        return self.filename

    @property
    def size_mb(self):
        return f"{self.size_bytes / (1024 * 1024):.2f} MB"

class ContactMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.name} - {self.subject}"

    class Meta:
        ordering = ['-created_at']

class TenantMetrics(models.Model):
    """
    Cached metrics for a tenant to speed up dashboard loading.
    Updated via signals on model changes.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name='metrics')
    
    total_products = models.PositiveIntegerField(default=0)
    total_orders = models.PositiveIntegerField(default=0)
    total_customers = models.PositiveIntegerField(default=0)
    total_branches = models.PositiveIntegerField(default=0)
    
    # Financial metrics (could be updated daily via Celery or on-demand)
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    total_customer_debt = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Metrics for {self.tenant.name}"

    class Meta:
        verbose_name_plural = "Tenant Metrics"

class FeedbackReport(models.Model):
    REPORT_TYPES = (
        ('bug', 'Bug Report'),
        ('recommendation', 'Recommendation'),
        ('feature_request', 'Feature Request'),
        ('other', 'Other'),
    )
    PRIORITIES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='feedback_reports')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='feedback_reports')
    
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, default='bug')
    priority = models.CharField(max_length=10, choices=PRIORITIES, default='medium')
    
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    # Status tracking for Puxbay admins
    status = models.CharField(max_length=20, choices=[
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ], default='new')
    admin_notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_report_type_display()}: {self.subject} ({self.tenant.name})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Feedback Report"
        verbose_name_plural = "Feedback Reports"
