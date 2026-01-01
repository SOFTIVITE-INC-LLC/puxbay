from django.db import models
from django.db.models import Avg
from django.contrib.auth.models import User
from accounts.models import Tenant, Branch
from main.models import Product, Customer
from utils.encryption import EncryptedTextField
import uuid

class StorefrontSettings(models.Model):
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name='storefront_settings')
    default_branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='storefront_settings')
    is_active = models.BooleanField(default=False, help_text="Is the online store visible to public?")
    slug = models.SlugField(unique=True, blank=True, null=True, help_text="e.g. 'my-shop'. If empty, uses tenant subdomain.")
    
    # Branding
    store_name = models.CharField(max_length=100, blank=True, help_text="DisplayName. Defaults to Tenant Name.")
    banner_image = models.ImageField(upload_to='store_banners/', blank=True, null=True)
    logo_image = models.ImageField(upload_to='store_logos/', blank=True, null=True)
    primary_color = models.CharField(max_length=7, default='#3b82f6', help_text="Hex code (e.g. #3b82f6)")
    
    # Content
    welcome_message = models.TextField(blank=True, default="Welcome to our online store!")
    about_text = models.TextField(blank=True)
    
    # Configuration
    allow_pickup = models.BooleanField(default=True)
    allow_delivery = models.BooleanField(default=False)
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    min_order_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    
    # Payment Configuration
    enable_stripe = models.BooleanField(default=False)
    stripe_public_key = EncryptedTextField(blank=True, null=True)
    stripe_secret_key = EncryptedTextField(blank=True, null=True)
    
    enable_paystack = models.BooleanField(default=False)
    paystack_public_key = EncryptedTextField(blank=True, null=True)
    paystack_secret_key = EncryptedTextField(blank=True, null=True)
    
    enable_mobile_money = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Store Settings for {self.tenant}"

class ProductImageGallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to='products/gallery/')
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

class ProductReview(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='product_reviews')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.name} - {self.product.name} ({self.rating}/5)"

class Wishlist(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('customer', 'product')

class Coupon(models.Model):
    DISCOUNT_TYPES = (
        ('percentage', 'Percentage (%)'),
        ('fixed', 'Fixed Amount'),
    )
    code = models.CharField(max_length=50, unique=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(default=100)
    used_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.code} ({self.value} {self.discount_type})"

class NewsletterSubscription(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('tenant', 'email')

class AbandonedCart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    email = models.EmailField()
    cart_data = models.JSONField(help_text="Stores the session cart contents")
    is_recovered = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Abandoned Cart: {self.email} ({self.tenant})"
