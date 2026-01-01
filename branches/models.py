from django.db import models
from accounts.models import Tenant, Branch, UserProfile
from main.models import Product, Supplier
import uuid
from utils.encryption import EncryptedTextField

class StockTransfer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS_CHOICES = (
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('shipped', 'Shipped'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    tenant = models.ForeignKey(Tenant, on_delete=models.DO_NOTHING, related_name='stock_transfers')
    source_branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='transfers_out')
    destination_branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='transfers_in')
    reference_id = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested', db_index=True)
    created_by = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, null=True, related_name='created_transfers')
    
    notes = EncryptedTextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.reference_id} ({self.source_branch} -> {self.destination_branch})"

class StockTransferItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transfer = models.ForeignKey(StockTransfer, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE) # Source Product
    quantity = models.PositiveIntegerField(default=1)
    transfer_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Price per unit for this transfer")

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class StockBatch(models.Model):
    """Specific batch/serial number for a product instance"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.DO_NOTHING, related_name='stock_batches')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='stock_batches')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='batches')
    batch_number = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=0)
    expiry_date = models.DateField(null=True, blank=True)
    received_date = models.DateField(auto_now_add=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    class Meta:
        verbose_name_plural = "Stock Batches"
        unique_together = ('branch', 'product', 'batch_number')
        ordering = ['expiry_date', 'received_date']

    def __str__(self):
        return f"{self.product.name} - {self.batch_number} (Qty: {self.quantity})"

    @property
    def is_expired(self):
        from django.utils import timezone
        if self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False

    def save(self, *args, **kwargs):
        if not self.id:
            # Assuming 'remaining_quantity' is a field that would be added to StockBatch
            # If not, this line would cause an AttributeError.
            # For now, I'll comment it out or assume it's intended to be added.
            # self.remaining_quantity = self.quantity 
            pass # Placeholder if remaining_quantity is not a field
        super().save(*args, **kwargs)



class StockMovement(models.Model):
    """Audit trail for all stock changes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    MOVEMENT_TYPES = (
        ('sale', 'Sale'),
        ('return', 'Return'),
        ('adjustment', 'Adjustment'),
        ('receive', 'PO Receive'),
        ('transfer_in', 'Transfer In'),
        ('transfer_out', 'Transfer Out'),
    )
    
    tenant = models.ForeignKey(Tenant, on_delete=models.DO_NOTHING)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='stock_movements')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='movements')
    batch = models.ForeignKey(StockBatch, on_delete=models.SET_NULL, null=True, blank=True, related_name='movements')
    
    quantity_change = models.IntegerField(help_text="Negative for deduction, Positive for addition")
    balance_after = models.IntegerField(help_text="Stock balance after transaction")
    
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES, db_index=True)
    reference = models.CharField(max_length=100, blank=True, help_text="Order ID, PO #, or Transfer ID")
    notes = EncryptedTextField(blank=True)
    
    created_by = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.movement_type}: {self.product.name} ({self.quantity_change})"


class PurchaseOrder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('ordered', 'Ordered'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    )
    
    tenant = models.ForeignKey(Tenant, on_delete=models.DO_NOTHING, related_name='purchase_orders')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='purchase_orders')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='orders')
    reference_id = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('card', 'Card'),
        ('mobile', 'Mobile Money'),
        ('credit', 'On Credit / Account'),
    )
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    notes = EncryptedTextField(blank=True, null=True)
    
    created_by = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, null=True, related_name='created_pos')
    created_at = models.DateTimeField(auto_now_add=True)
    expected_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.reference_id} - {self.supplier.name}"

class PurchaseOrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    po = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class CashDrawerSession(models.Model):
    """Tracks daily cash drawer sessions for reconciliation"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('closed', 'Closed'),
    )

    tenant = models.ForeignKey(Tenant, on_delete=models.DO_NOTHING, related_name='cash_sessions')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='cash_sessions')
    employee = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, null=True, related_name='cash_sessions')
    
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    
    starting_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    expected_cash = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Calculated from sales")
    actual_cash = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Counted by employee")
    difference = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    notes = EncryptedTextField(blank=True)

    def __str__(self):
        return f"Session {self.id} - {self.branch.name} ({self.status})"

class StocktakeSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='stocktakes')
    created_by = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('in_progress', 'In Progress'), ('completed', 'Completed')], default='in_progress')
    access_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Stocktake {self.started_at.date()} - {self.branch.name}"

class StocktakeEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(StocktakeSession, on_delete=models.CASCADE, related_name='entries')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stocktake_entries')
    counted_quantity = models.IntegerField(default=0)
    expected_quantity = models.IntegerField(default=0, help_text="System stock at time of count")
    notes = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('session', 'product')

    @property
    def difference(self):
        return self.counted_quantity - self.expected_quantity

    @property
    def difference_value(self):
        return self.difference * self.product.cost_price

    def __str__(self):
        return f"{self.product.name} - Counted: {self.counted_quantity}"

class Shift(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='shifts')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='shifts')
    staff = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, related_name='shifts')
    
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    status = models.CharField(max_length=20, choices=[
        ('scheduled', 'Scheduled'),
        ('checked_in', 'Checked In'),
        ('completed', 'Completed'),
        ('absent', 'Absent'),
    ], default='scheduled')
    
    role = models.CharField(max_length=50, blank=True, null=True, help_text="Specific role for this shift (e.g., Cashier, Floor)")
    notes = models.TextField(blank=True, null=True)
    
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    
    is_for_bid = models.BooleanField(default=False, help_text="Available for any qualified staff to claim")
    requested_swap_with = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='swap_requests_received')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f"{self.staff.user.username} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"

class InventoryRecommendation(models.Model):
    """Predictive analysis results for inventory reordering"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='inventory_recommendations')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='inventory_recommendations')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reorder_recommendations')
    
    predicted_velocity = models.DecimalField(max_digits=10, decimal_places=2, help_text="Average daily sales velocity")
    current_stock = models.IntegerField()
    estimated_days_left = models.IntegerField(help_text="Days until stockout")
    recommended_reorder_quantity = models.IntegerField()
    
    is_dismissed = models.BooleanField(default=False)
    last_analyzed_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['estimated_days_left']
        unique_together = ('branch', 'product')

    def __str__(self):
        return f"Reorder {self.product.name} (Qty: {self.recommended_reorder_quantity})"
