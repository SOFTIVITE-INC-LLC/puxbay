from django.db import models
from django.contrib.auth import get_user_model
import uuid
from utils.encryption import EncryptedTextField

User = get_user_model()

class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    TYPE_CHOICES = (
        ('info', 'Info'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    )

    CATEGORY_CHOICES = (
        ('general', 'General'),
        ('inventory', 'Inventory'),
        ('sales', 'Sales'),
        ('security', 'Security'),
        ('system', 'System'),
    )

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = EncryptedTextField()
    link = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.recipient.username}"

class NotificationSetting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_settings')
    email_notifications = models.BooleanField(default=True)
    low_stock_alerts = models.BooleanField(default=True)
    sales_reports = models.BooleanField(default=True)
    security_alerts = models.BooleanField(default=True) # Large refunds, voids
    system_alerts = models.BooleanField(default=True) # Backup, Disk usage
    
    def __str__(self):
        return f"Settings for {self.user.username}"
