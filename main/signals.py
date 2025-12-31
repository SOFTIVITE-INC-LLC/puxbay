from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import F
from .models import Order, Customer, Product, TenantMetrics
from accounts.models import Branch, Tenant
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from utils.webhooks import WebhookService

@receiver(post_save, sender=Order)
def notify_new_order(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        if instance.tenant:
            group_name = f"tenant_{instance.tenant.id}"
            
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'send_notification',
                    'title': 'New Order Received',
                    'message': f'Order #{instance.order_number} - {instance.total_amount}',
                    'level': 'success'
                }
            )

@receiver(post_save, sender=Order)
def order_webhook_trigger(sender, instance, created, **kwargs):
    """Trigger order.created webhook when a new order is completed"""
    if created and instance.status == 'completed':
        payload = {
            'order_id': str(instance.id),
            'order_number': instance.order_number,
            'total_amount': str(instance.total_amount),
            'customer': instance.customer.name if instance.customer else 'Guest',
            'created_at': instance.created_at.isoformat()
        }
        WebhookService.trigger(instance.tenant, 'order.created', payload)

@receiver(post_save, sender=Customer)
def customer_webhook_trigger(sender, instance, created, **kwargs):
    """Trigger customer.registered webhook"""
    if created:
        payload = {
            'customer_id': str(instance.id),
            'name': instance.name,
            'email': instance.email,
            'created_at': instance.created_at.isoformat()
        }
        WebhookService.trigger(instance.tenant, 'customer.registered', payload)

@receiver(post_save, sender=Product)
def inventory_low_webhook_trigger(sender, instance, **kwargs):
    """Trigger inventory.low webhook when stock falls below threshold"""
    if instance.is_active and instance.stock_quantity <= instance.low_stock_threshold:
        # Check if we've already triggered this recently? 
        # For simplicity, we trigger on every low-stock save
        payload = {
            'product_id': str(instance.id),
            'name': instance.name,
            'sku': instance.sku,
            'stock_quantity': instance.stock_quantity,
            'threshold': instance.low_stock_threshold
        }
        WebhookService.trigger(instance.tenant, 'inventory.low', payload)

@receiver(post_save, sender=Tenant)
def create_tenant_metrics(sender, instance, created, **kwargs):
    """Ensure every tenant has a metrics object"""
    if created:
        TenantMetrics.objects.get_or_create(tenant=instance)

@receiver(post_save, sender=Product)
def update_product_metrics(sender, instance, created, **kwargs):
    if created and instance.tenant:
        metrics, _ = TenantMetrics.objects.get_or_create(tenant=instance.tenant)
        TenantMetrics.objects.filter(id=metrics.id).update(total_products=F('total_products') + 1)

@receiver(post_delete, sender=Product)
def decrement_product_metrics(sender, instance, **kwargs):
    if instance.tenant:
        TenantMetrics.objects.filter(tenant=instance.tenant).update(total_products=F('total_products') - 1)

@receiver(post_save, sender=Order)
def update_order_metrics(sender, instance, created, **kwargs):
    if created and instance.tenant:
        metrics, _ = TenantMetrics.objects.get_or_create(tenant=instance.tenant)
        TenantMetrics.objects.filter(id=metrics.id).update(total_orders=F('total_orders') + 1)

@receiver(post_delete, sender=Order)
def decrement_order_metrics(sender, instance, **kwargs):
    if instance.tenant:
        TenantMetrics.objects.filter(tenant=instance.tenant).update(total_orders=F('total_orders') - 1)

@receiver(post_save, sender=Customer)
def update_customer_metrics(sender, instance, created, **kwargs):
    if created and instance.tenant:
        metrics, _ = TenantMetrics.objects.get_or_create(tenant=instance.tenant)
        TenantMetrics.objects.filter(id=metrics.id).update(total_customers=F('total_customers') + 1)

@receiver(post_delete, sender=Customer)
def decrement_customer_metrics(sender, instance, **kwargs):
    if instance.tenant:
        TenantMetrics.objects.filter(tenant=instance.tenant).update(total_customers=F('total_customers') - 1)

@receiver(post_save, sender=Branch)
def update_branch_metrics(sender, instance, created, **kwargs):
    if created and instance.tenant:
        metrics, _ = TenantMetrics.objects.get_or_create(tenant=instance.tenant)
        TenantMetrics.objects.filter(id=metrics.id).update(total_branches=F('total_branches') + 1)

@receiver(post_delete, sender=Branch)
def decrement_branch_metrics(sender, instance, **kwargs):
    if instance.tenant:
        TenantMetrics.objects.filter(tenant=instance.tenant).update(total_branches=F('total_branches') - 1)
