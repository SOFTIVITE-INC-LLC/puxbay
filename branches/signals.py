from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from main.models import Product, Order, Return
from notifications.utils import send_notification

User = get_user_model()

@receiver(post_save, sender=Product)
def check_low_stock(sender, instance, **kwargs):
    if instance.stock_quantity <= instance.low_stock_threshold:
        # Notify admins/managers of that branch
        # This is a bit expensive if done constantly, but fine for MVP
        
        # Find relevant users: Admin of the tenant, or Manager of the branch
        users = User.objects.filter(
            profiles__tenant=instance.tenant, 
            profiles__role__in=['admin', 'manager']
        ).distinct()
        
        if instance.branch:
            users = users.filter(profiles__branch=instance.branch) | users.filter(profiles__role='admin')
        
        for user in users:
            send_notification(
                user=user,
                title=f"Low Stock Alert: {instance.name}",
                message=f"Product {instance.name} is low on stock ({instance.stock_quantity} remaining). Threshold: {instance.low_stock_threshold}.",
                level='warning',
                category='inventory',
                link=f"/branches/{instance.branch.id}/products/" if instance.branch else None
            )

@receiver(post_save, sender=Return)
def check_large_refund(sender, instance, created, **kwargs):
    if instance.refund_amount > 100: # Configuration threshold? Hardcoded for now.
        # Notify Admins only
        admins = User.objects.filter(profiles__tenant=instance.tenant, profiles__role='admin')
        
        for admin in admins:
            send_notification(
                user=admin,
                title=f"Large Refund Detected: ${instance.refund_amount}",
                message=f"A large refund of ${instance.refund_amount} was processed for Order #{instance.order.id}.",
                level='warning',
                category='security',
                link=f"/branches/{instance.branch.id}/reports/financial/" # Placeholder link
            )

@receiver(post_save, sender=Order)
def check_order_cancellation(sender, instance, created, **kwargs):
    if instance.status == 'cancelled':
        # Notify Admins
        admins = User.objects.filter(profiles__tenant=instance.tenant, profiles__role='admin')
        
        for admin in admins:
            send_notification(
                user=admin,
                title=f"Order Cancelled: #{instance.id}",
                message=f"Order #{instance.id} for ${instance.total_amount} was cancelled.",
                level='info',
                category='security'
            )
