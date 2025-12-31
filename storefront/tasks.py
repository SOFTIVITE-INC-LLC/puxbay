from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import AbandonedCart, StorefrontSettings
from main.models import Product
from accounts.models import Tenant

@shared_task
def process_abandoned_carts():
    """Identify carts abandoned between 2 and 48 hours ago and trigger recovery emails."""
    now = timezone.now()
    threshold = now - timedelta(hours=2)
    limit = now - timedelta(hours=48)
    
    abandoned_carts = AbandonedCart.objects.filter(
        is_recovered=False,
        email_sent=False,
        updated_at__lte=threshold,
        updated_at__gte=limit
    )
    
    for cart in abandoned_carts:
        send_recovery_email.delay(cart.id)

@shared_task
def send_recovery_email(cart_id):
    """Sends a recovery email for a specific abandoned cart."""
    try:
        cart = AbandonedCart.objects.get(id=cart_id)
        tenant = cart.tenant
        store_settings = StorefrontSettings.objects.filter(tenant=tenant).first()
        
        # Resolve products to show in email
        cart_items = []
        product_ids = cart.cart_data.keys()
        products = Product.objects.filter(id__in=product_ids)
        product_map = {str(p.id): p for p in products}
        
        for pid, qty in cart.cart_data.items():
            product = product_map.get(str(pid))
            if product:
                cart_items.append({
                    'name': product.name,
                    'quantity': qty,
                    'price': product.price
                })

        # Build recovery URL - Pointing to the recovery view (yet to be implemented)
        # Assuming domain is handled by settings or subdomain logic
        recover_url = f"{settings.DOMAIN_URL.rstrip('/')}/store/recover-cart/{cart.id}/"
        
        context = {
            'cart': cart,
            'cart_items': cart_items,
            'store_settings': store_settings,
            'recover_url': recover_url,
            'tenant': tenant,
            'timestamp': timezone.now(),
        }
        
        subject = f"{settings.EMAIL_SUBJECT_PREFIX}Did you forget something?"
        html_message = render_to_string('storefront/emails/abandoned_cart_recovery.html', context)
        
        send_mail(
            subject,
            f"You left some items in your cart at {store_settings.store_name if store_settings else tenant.name}. Visit {recover_url} to restore them.",
            settings.DEFAULT_FROM_EMAIL,
            [cart.email],
            html_message=html_message
        )
        
        cart.email_sent = True
        cart.save()
        return f"Recovery email sent to {cart.email}"
    except Exception as e:
        return f"Error: {str(e)}"
