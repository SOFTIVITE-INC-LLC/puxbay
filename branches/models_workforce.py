from django.db import models
from accounts.models import Tenant, Branch, UserProfile
import uuid

class CommissionRule(models.Model):
    """Tiered commission logic for staff sales"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='commission_rules')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True, related_name='commission_rules')
    
    name = models.CharField(max_length=100)
    min_sales_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    flat_bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.commission_percentage}%)"

class StaffAchievement(models.Model):
    """Earned badges and milestones for staff members"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    staff = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, related_name='achievements')
    
    badge_name = models.CharField(max_length=100)
    badge_icon = models.CharField(max_length=50, default='stars') # Material icon name
    description = models.TextField(blank=True)
    
    earned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.staff.user.username} - {self.badge_name}"

class ShiftSwapRequest(models.Model):
    """Handles employee-led shift exchange logic"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requesting_staff = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, related_name='sent_swap_requests')
    target_staff = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='received_swap_requests')
    
    # Using 'branches.Shift' as string to avoid circular imports if any, 
    # though they are in the same app.
    original_shift = models.ForeignKey('branches.Shift', on_delete=models.CASCADE, related_name='swap_requests')
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Swap Request by {self.requesting_staff.user.username}"
