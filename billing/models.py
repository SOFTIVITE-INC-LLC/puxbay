from django.db import models
from tinymce.models import HTMLField
from accounts.models import Tenant
import uuid

class Plan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    INTERVAL_CHOICES = [
        ('monthly', 'Monthly'),
        ('6-month', '6 Months'),
        ('yearly', 'Yearly'),
    ]
    
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price_ghs = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Price in GHS (regional pricing)")
    interval = models.CharField(max_length=20, choices=INTERVAL_CHOICES, default='monthly')
    trial_days = models.PositiveIntegerField(default=7, help_text="Number of trial days")
    stripe_price_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Limits
    max_branches = models.PositiveIntegerField(default=1, help_text="Maximun number of branches allowed")
    max_users = models.PositiveIntegerField(default=1, help_text="Maximum number of users allowed")
    api_access = models.BooleanField(default=False, help_text="Whether API access is allowed")
    api_daily_limit = models.PositiveIntegerField(default=0, help_text="Daily API request limit")
    
    # Features (Simple JSON implementation for now)
    features = models.JSONField(default=dict, blank=True, help_text="JSON object of features enabled")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (${self.price}/{self.interval})"

    def save(self, *args, **kwargs):
        
        super().save(*args, **kwargs)

class Subscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('trialing', 'Trialing'),
        ('canceled', 'Canceled'),
        ('incomplete', 'Incomplete'),
    ]

    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, related_name='subscriptions')
    stripe_subscription_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trialing')
    current_period_end = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    
    # API Usage Tracking
    api_requests_today = models.PositiveIntegerField(default=0, help_text="API requests made today")
    api_requests_this_month = models.PositiveIntegerField(default=0, help_text="API requests this month")
    api_last_reset_date = models.DateField(auto_now_add=True, help_text="Last daily reset date")
    api_month_reset_date = models.DateField(auto_now_add=True, help_text="Last monthly reset date")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tenant.name} - {self.plan.name if self.plan else 'No Plan'}"

class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_invoice_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, default='succeeded')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.amount} - {self.status}"

class PricingPlan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    description = models.TextField(blank=True)
    is_popular = models.BooleanField(default=False)
    button_text = models.CharField(max_length=50, default='Get Started')
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

class PlanFeature(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan = models.ForeignKey(PricingPlan, on_delete=models.CASCADE, related_name='features')
    text = models.CharField(max_length=255)
    is_available = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.plan.name} - {self.text}"

class FAQ(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question

class PaymentGatewayConfig(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True, help_text="stripe, paystack, or paypal")
    is_active = models.BooleanField(default=True)
    description = models.CharField(max_length=255, blank=True)
    
    class Meta:
        verbose_name = "Payment Gateway Configuration"
        verbose_name_plural = "Payment Gateway Configurations"

    def __str__(self):
        return f"{self.name} ({'Active' if self.is_active else 'Inactive'})"

class LegalDocument(models.Model):
    """Dynamic legal documents like Terms of Service, Privacy Policy, etc."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, help_text="e.g., 'terms-of-service', 'privacy-policy'")
    content = HTMLField(help_text="The main body of the document")
    is_published = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        verbose_name = "Legal Document"
        verbose_name_plural = "Legal Documents"

class BlogCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Blog Category"
        verbose_name_plural = "Blog Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

class BlogTag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Blog Tag"
        verbose_name_plural = "Blog Tags"
        ordering = ['name']

    def __str__(self):
        return self.name

class BlogPost(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=255)
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='blog_posts')
    featured_image = models.ImageField(upload_to='blog/featured/', blank=True, null=True)
    excerpt = models.TextField(help_text="A short summary of the post")
    content = HTMLField()
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, related_name='posts')
    tags = models.ManyToManyField(BlogTag, blank=True, related_name='posts')
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.status == 'published' and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

class FeatureCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, help_text="Material symbol name (e.g., 'grid_view')")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Feature Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class FeatureItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(FeatureCategory, on_delete=models.CASCADE, related_name='features')
    title = models.CharField(max_length=200)
    desc = models.TextField()
    icon = models.CharField(max_length=50, help_text="Material symbol name (e.g., 'point_of_sale')")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # Link to a potential full documentation or details page if needed
    details_url = models.CharField(max_length=255, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return f"{self.category.name} - {self.title}"

class LeadershipMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=150)
    image = models.ImageField(upload_to='leadership/', help_text="Member portrait (recommended 800x800)")
    bio = models.TextField(blank=True, null=True)
    
    # Social Links
    linkedin_url = models.URLField(blank=True, null=True, help_text="Full LinkedIn profile URL")
    twitter_url = models.URLField(blank=True, null=True, help_text="Full Twitter/X profile URL")
    
    order = models.PositiveIntegerField(default=0, help_text="Display order (lower is first)")
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Leadership Member"
        verbose_name_plural = "Leadership Members"

    def __str__(self):
        return f"{self.name} - {self.role}"
