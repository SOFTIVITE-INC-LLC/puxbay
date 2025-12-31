from django.db import models
from django.contrib.auth.models import User
import uuid
from utils.encryption import EncryptedTextField
from django_tenants.models import TenantMixin, DomainMixin

class Tenant(TenantMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    subdomain = models.CharField(max_length=100, unique=True, help_text="Used for schema name")
    created_on = models.DateField(auto_now_add=True)
    
    TENANT_TYPES = (
        ('standard', 'Standard Merchant'),
    )
    tenant_type = models.CharField(
        max_length=20, 
        choices=TENANT_TYPES, 
        default='standard',
        help_text="Classification for analytics and billing"
    )
    
    logo = models.ImageField(upload_to='tenant_logos/', null=True, blank=True, help_text="Company logo for branding")
    address = EncryptedTextField(blank=True, null=True)
    pos_api_key = EncryptedTextField(blank=True, null=True, help_text="Stored raw key for internal POS use")
    is_sandbox = models.BooleanField(default=False, help_text="Is this a test/sandbox environment?")
    sandbox_wipe_at = models.DateTimeField(null=True, blank=True, help_text="When this sandbox data should be wiped/deleted")
    
    # Auto create schema when tenant is saved
    auto_create_schema = True
    
    def save(self, *args, **kwargs):
        if not self.schema_name and self.subdomain:
            self.schema_name = self.subdomain.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Domain(DomainMixin):
    pass

class Branch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=100)
    unique_id = EncryptedTextField(max_length=20, unique=True, db_index=True, blank=True, null=True, help_text="Human-readable branch identifier (e.g., BR-0001)")
    address = EncryptedTextField(blank=True, null=True)
    phone = EncryptedTextField(blank=True, null=True) # Phone is PII
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Settings
    logo = models.ImageField(upload_to='branch_logos/', null=True, blank=True, help_text="Branch logo for receipts")
    low_stock_threshold = models.PositiveIntegerField(default=10)
    currency_symbol = models.CharField(max_length=5, default='$')
    CURRENCY_CHOICES = (
        ('USD', 'USD - US Dollar'),
        ('NGN', 'NGN - Nigerian Naira'),
        ('GHS', 'GHS - Ghanaian Cedi'),
        ('ZAR', 'ZAR - South African Rand'),
        ('EUR', 'EUR - Euro'),
        ('GBP', 'GBP - British Pound'),
    )
    currency_code = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    receipt_header = models.TextField(blank=True, null=True, help_text="Text to appear at top of receipts")

    receipt_footer = models.TextField(blank=True, null=True, help_text="Text to appear at bottom of receipts")
    
    BRANCH_TYPES = (
        ('retail', 'Retail'),
        ('wholesale', 'Wholesale'),
    )
    branch_type = models.CharField(max_length=20, choices=BRANCH_TYPES, default='retail')
    
    # Sync Health Monitoring
    last_sync_at = models.DateTimeField(null=True, blank=True, help_text="Last successful sync timestamp")
    sync_status = models.CharField(
        max_length=20,
        choices=[('healthy', 'Healthy'), ('warning', 'Warning'), ('error', 'Error')],
        default='healthy',
        help_text="Current sync health status"
    )
    pending_sync_count = models.PositiveIntegerField(default=0, help_text="Number of pending sync items")
    sync_error_message = models.TextField(blank=True, null=True, help_text="Last sync error if any")

    class Meta:
        verbose_name_plural = "Branches"

    def __str__(self):
        if self.unique_id:
            return f"{self.unique_id} - {self.name}"
        return f"{self.name} - {self.tenant.name}"

class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profiles')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='users')
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    role = models.CharField(max_length=50, choices=[
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('procurement_manager', 'Procurement Manager'),
        ('sales', 'Sales Person'),
        ('financial', 'Financial'),
        ('supplier', 'Supplier'),
    ], default='sales', db_index=True)
    
    can_perform_credit_sales = models.BooleanField(
        default=False, 
        help_text="Designates whether the salesperson can process transactions using credit as a payment method."
    )
    
    # Security & Fast Access
    is_2fa_enabled = models.BooleanField(default=False)
    otp_secret = EncryptedTextField(blank=True, null=True)
    pos_pin = EncryptedTextField(blank=True, null=True, help_text="4-6 digit numeric PIN for fast POS access")
    
    # Email Verification
    is_email_verified = models.BooleanField(default=False, help_text="Has the user verified their email address?")

    class Meta:
        unique_together = ('user', 'tenant')

    @property
    def profile(self):
        """Backwards compatibility helper (returns self)"""
        return self

    def __str__(self):
        return f"{self.user.username} - {self.tenant.name}"

class Attendance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='attendance_records')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='attendance_records')
    clock_in = models.DateTimeField(auto_now_add=True)
    clock_out = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.user.username} - {self.clock_in.date()}"
        
    @property
    def duration(self):
        if self.clock_out:
            return self.clock_out - self.clock_in
        return None

class ActivityLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ACTION_TYPES = (
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('export', 'Data Export'),
        ('backup', 'Data Backup'),
    )
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='activity_logs')
    actor = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='actions')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    target_model = models.CharField(max_length=100, blank=True)
    target_object_id = models.CharField(max_length=100, blank=True)
    description = EncryptedTextField() # Log details might be sensitive
    changes = models.JSONField(null=True, blank=True, help_text="Detailed field-level changes (Old vs New)")
    ip_address = EncryptedTextField(blank=True, null=True) # PII
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.actor} - {self.action_type} - {self.timestamp}"

class SystemLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    LEVEL_CHOICES = (
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    )

    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    module = models.CharField(max_length=255)
    message = EncryptedTextField() # Logs might contain PII
    traceback = EncryptedTextField(blank=True, null=True)
    path = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'System Log'
        verbose_name_plural = 'System Logs'

    def __str__(self):
        return f"{self.level} - {self.module} - {self.created_at}"

class GlobalOrder(models.Model):
    """
    aggregated read-only copy of orders from all tenants for the Superuser dashboard.
    Populated via signals from main.models.Order.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) # Maps to tenant Order ID
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='global_orders')
    
    # Snapshot of Order Data
    customer_name = EncryptedTextField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField() # From original order
    
    synced_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Global Order (Synced)"
        verbose_name_plural = "Global Orders (Synced)"

    def __str__(self):
        return f"{self.tenant.name} - {self.total_amount} - {self.status}"

class CrossTenantAuditLog(models.Model):
    """Track superuser actions when accessing different tenants"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    ACTION_TYPES = (
        ('access', 'Accessed Tenant'),
        ('view', 'Viewed Object'),
        ('add', 'Added Object'),
        ('change', 'Changed Object'),
        ('delete', 'Deleted Object'),
    )
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='cross_tenant_actions')
    accessed_tenant = models.ForeignKey(Tenant, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    user_home_tenant = models.ForeignKey(Tenant, on_delete=models.SET_NULL, null=True, related_name='user_audit_logs', help_text="User's original tenant")
    
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    target_model = models.CharField(max_length=100, blank=True, help_text="Model that was accessed/modified")
    target_object_id = models.CharField(max_length=100, blank=True, help_text="ID of the object")
    target_object_repr = models.CharField(max_length=200, blank=True, help_text="String representation of object")
    
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Cross-Tenant Audit Log"
        verbose_name_plural = "Cross-Tenant Audit Logs"
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['accessed_tenant', '-timestamp']),
            models.Index(fields=['action_type', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username if self.user else 'Unknown'} - {self.get_action_type_display()} - {self.accessed_tenant.name if self.accessed_tenant else 'Unknown'}"

class APIKey(models.Model):
    """Secure API keys for external integrations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='api_keys')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='api_keys', null=True, blank=True)
    
    name = models.CharField(max_length=100, help_text="Label for the key (e.g., 'Mobile App')")
    key_prefix = models.CharField(max_length=8, editable=False)
    key_hash = models.CharField(max_length=128, editable=False, help_text="SHA-256 hash of the full key")
    
    is_active = models.BooleanField(default=True)
    is_sandbox = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"
        indexes = [
            models.Index(fields=['key_prefix']),
        ]

    def __str__(self):
        return f"{self.name} ({self.tenant.name})"

class ExternalSystem(models.Model):
    """External systems/apps registered by developers"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    developer = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='registered_systems')
    
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    
    client_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    client_secret_hash = models.CharField(max_length=128, editable=False)
    
    # Standard OAuth2/Webhook fields
    redirect_uris = models.JSONField(default=list, blank=True, help_text="List of allowed redirect URIs")
    webhook_url = models.URLField(blank=True, null=True)
    
    icon = models.CharField(max_length=50, default="rocket_launch", help_text="Material symbol name for the icon")
    is_public = models.BooleanField(default=False, help_text="Make this app available in the Marketplace")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} by {self.developer.name}"

class WebhookEndpoint(models.Model):
    """Developer-managed webhook endpoints"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='webhook_endpoints')
    external_system = models.ForeignKey(ExternalSystem, on_delete=models.SET_NULL, null=True, blank=True, related_name='webhooks')
    
    url = models.URLField(help_text="The URL where we will send POST requests")
    secret = models.CharField(max_length=64, help_text="Used to sign the webhook payload")
    
    is_active = models.BooleanField(default=True)
    events = models.JSONField(default=list, help_text="List of subscribed events (e.g., ['order.created', 'inventory.low'])")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.url} ({self.tenant.name})"

class WebhookEvent(models.Model):
    """Log of webhook delivery attempts"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    endpoint = models.ForeignKey(WebhookEndpoint, on_delete=models.CASCADE, related_name='delivery_logs')
    event_type = models.CharField(max_length=50) # e.g., 'order.created'
    
    payload = models.JSONField()
    signature = models.CharField(max_length=128, blank=True, null=True, help_text="HMAC-SHA256 signature of payload")
    status_code = models.PositiveIntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.event_type} to {self.endpoint.url} - {self.status_code}"



# Audit Logging Models
class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    action = models.CharField(max_length=50) # create, update, delete, login, logout, etc.
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, blank=True, null=True)
    changes = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='account_audit_logs', null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp', 'action']),
            models.Index(fields=['user', 'action']),
        ]

    def __str__(self):
        return f"{self.action} - {self.model_name} - {self.timestamp}"

class APIRequestLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='api_logs')
    method = models.CharField(max_length=10)
    endpoint = models.CharField(max_length=255, db_index=True)
    status_code = models.PositiveIntegerField(null=True, blank=True)
    response_time_ms = models.PositiveIntegerField(null=True, blank=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='api_logs', null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    request_body = models.JSONField(default=dict, blank=True)
    response_body = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp', 'endpoint']),
            models.Index(fields=['status_code']),
        ]

    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code}"
class SEOSettings(models.Model):
    """Global SEO settings for each tenant's storefront/public presence"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name='seo_settings')
    
    meta_title = models.CharField(max_length=150, blank=True, null=True, help_text="Default page title for search engines")
    meta_description = models.TextField(blank=True, null=True, help_text="Short summary of the site for search results")
    keywords = models.CharField(max_length=255, blank=True, null=True, help_text="Comma-separated keywords")
    
    # Open Graph / Social
    og_title = models.CharField(max_length=150, blank=True, null=True, help_text="Title shown when sharing on social media")
    og_description = models.TextField(blank=True, null=True, help_text="Description shown when sharing")
    og_image = models.ImageField(upload_to='seo/og_images/', blank=True, null=True, help_text="Image shown when sharing (1200x630 recommended)")
    
    # Verification & Tracking
    google_analytics_id = models.CharField(max_length=50, blank=True, null=True, help_text="G-XXXXXXXXXX")
    facebook_pixel_id = models.CharField(max_length=50, blank=True, null=True)
    
    # Homepage Settings
    homepage_video_id = models.CharField(max_length=50, blank=True, null=True, default='dQw4w9WgXcQ', help_text="YouTube Video ID for the homepage demo (e.g., dQw4w9WgXcQ)")
    
    # Contact Information
    contact_email = models.EmailField(blank=True, null=True, default='info@puxbay.com')
    support_email = models.EmailField(blank=True, null=True, default='support@puxbay.com')
    contact_phone = models.CharField(max_length=50, blank=True, null=True, default='+1 (555) 123-4567')
    contact_address = models.TextField(blank=True, null=True, default='123 Tech Boulevard, Suite 400\nSan Francisco, CA 94107')
    office_hours = models.CharField(max_length=100, blank=True, null=True, default='Mon-Fri 9am-5pm EST')
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "SEO Setting"
        verbose_name_plural = "SEO Settings"

    def __str__(self):
        return f"SEO - {self.tenant.name}"
